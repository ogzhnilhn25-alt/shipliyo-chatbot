from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Chatbot modüllerini import et
from chatbot_manager import ChatbotManager

# Çevre değişkenlerini yükle
load_dotenv()

app = Flask(__name__)
CORS(app)

# MongoDB bağlantısı
MONGO_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
client = MongoClient(MONGO_URI)
db = client.shipliyo_sms

# Chatbot yöneticisi
chatbot = ChatbotManager()

# ✅ WEB ARAYÜZÜ
@app.route('/')
def home():
    """Ana sayfa - web arayüzü"""
    return render_template('index.html')

# ✅ CHATBOT ENDPOINT
@app.route('/api/chatbot', methods=['POST'])
def chatbot_handler():
    """Chatbot mesaj işleyici"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        session_id = data.get('session_id', 'default')
        language = data.get('language', 'tr')

        print(f"\n🎯 CHATBOT REQUEST: '{message}'")
        print(f"🎯 Session: {session_id}, Language: {language}")

        response = chatbot.handle_message(message, session_id, language)

        print(f"🎯 CHATBOT RESPONSE: Success={response['success']}")
        print(f"🎯 Message: {response['response']}")
        print("─" * 60)

        return jsonify(response)

    except Exception as e:
        print(f"❌ CHATBOT ERROR: {str(e)}")
        return jsonify({
            "success": False,
            "response": f"Hata oluştu: {str(e)}",
            "response_type": "direct"
        }), 500

# ✅ DESTEKLENEN DİLLER
@app.route('/api/languages', methods=['GET'])
def supported_languages():
    return jsonify({
        "success": True,
        "languages": [
            {"code": "tr", "name": "Türkçe", "flag": "🇹🇷"},
            {"code": "bg", "name": "Bulgarca", "flag": "🇧🇬"},
            {"code": "en", "name": "İngilizce", "flag": "🇺🇸"}
        ]
    })

# ✅ SMS GATEWAY (Android uygulaması buraya POST eder)
@app.route('/gateway-sms', methods=['POST'])
def gateway_sms():
    """Android'den gelen SMS'leri alır, MongoDB'ye kaydeder ve Chatbot'a gönderir"""
    try:
        data = request.get_json()
        from_number = data.get('from')
        body = data.get('body')
        device_id = data.get('deviceId', 'unknown')

        # 🔎 Boş mesaj kontrolü
        if not body or not from_number:
            print(⚠️ Eksik SMS verisi alındı.")
            return jsonify({"status": "error", "message": "Eksik SMS verisi"}), 400

        # 🔁 Duplicate kontrolü
        time_threshold = datetime.now() - timedelta(seconds=10)
        existing_sms = db.sms_messages.find_one({
            'from': from_number,
            'body': body,
            'timestamp': {'$gte': time_threshold}
        })

        if existing_sms:
            print(f"⏭️ DUPLICATE SMS - Zaten kayıtlı: {existing_sms['_id']}")
            return jsonify({
                "status": "success",
                "message": "SMS alındı (duplicate - zaten kayıtlı)"
            }), 200

        # 📝 Yeni SMS kaydı
        sms_data = {
            'from': from_number,
            'body': body,
            'timestamp': datetime.now(),
            'device_id': device_id,
            'processed': False,
            'created_at': datetime.now(),
            'source': 'gateway',
            'chatbot_response': None
        }

        result = db.sms_messages.insert_one(sms_data)
        sms_id = str(result.inserted_id)

        print("\n📩 YENİ SMS ALINDI:")
        print(f"📱 Gönderen: {from_number}")
        print(f"💬 Mesaj: {body}")
        print(f"📦 Cihaz ID: {device_id}")
        print(f"🆔 Mongo ID: {sms_id}")
        print("─" * 60)

        # 💬 Chatbot'a gönder
        try:
            chatbot_response = chatbot.handle_message(body, session_id=from_number, language='tr')
            chatbot_text = chatbot_response.get('response', '')

            print(f"🤖 Chatbot Yanıtı: {chatbot_text}")

            # 🔄 MongoDB kaydını güncelle
            db.sms_messages.update_one(
                {'_id': result.inserted_id},
                {'$set': {
                    'processed': True,
                    'chatbot_response': chatbot_text,
                    'processed_at': datetime.now()
                }}
            )

        except Exception as chat_err:
            print(f"❌ Chatbot işleme hatası: {chat_err}")

        return jsonify({
            "status": "success",
            "message": "SMS işlendi ve kaydedildi",
            "sms_id": sms_id
        }), 200

    except Exception as e:
        print(f"❌ GATEWAY HATASI: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Sistem hatası: {str(e)}"
        }), 500

# ✅ TEST İÇİN: SMS LİSTELE
@app.route('/api/sms', methods=['GET'])
def get_sms():
    try:
        sms_list = list(db.sms_messages.find().sort('timestamp', -1).limit(10))
        for sms in sms_list:
            sms['_id'] = str(sms['_id'])
            if 'timestamp' in sms:
                sms['timestamp'] = sms['timestamp'].isoformat()
        return jsonify({
            "success": True,
            "count": len(sms_list),
            "sms_list": sms_list
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ✅ SAĞLIK KONTROLÜ
@app.route('/health', methods=['GET'])
def health_check():
    try:
        client.admin.command('ismaster')
        db_status = "connected"
    except:
        db_status = "disconnected"
    return jsonify({
        "status": "healthy",
        "service": "Shipliyo SMS Backend & Chatbot",
        "timestamp": datetime.now().isoformat(),
        "database": db_status,
        "version": "2.1.0"
    })

# ✅ Uygulamayı başlat
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    print(f"\n🚀 Shipliyo Backend & Chatbot running on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
