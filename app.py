from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Chatbot modüllerini import edin
from chatbot_manager import ChatbotManager

# Çevre değişkenlerini yükle
load_dotenv()

app = Flask(__name__)
CORS(app)

# MongoDB bağlantısı
MONGO_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
client = MongoClient(MONGO_URI)
db = client.shipliyo_sms

# Chatbot manager
chatbot = ChatbotManager()

# Shipliyo API Routes - Qukasoft Entegrasyonu
@app.route('/api/shipliyo/chatbot', methods=['POST'])
def chatbot_api():
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "response": "Geçersiz JSON verisi",
                "response_type": "direct"
            }), 400
        
        message = data.get('message', '').strip()
        session_id = data.get('session_id', 'default_session')
        language = data.get('language', 'tr')
        
        if not message:
            return jsonify({
                "success": False, 
                "response": "Mesaj boş olamaz",
                "response_type": "direct"
            }), 400
        
        # Mevcut chatbot manager'ını kullan
        from chatbot_manager import ChatbotManager
        chatbot = ChatbotManager()
        response = chatbot.handle_message(message, session_id, language)
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            "success": False,
            "response": f"API hatası: {str(e)}",
            "response_type": "direct"
        }), 500

@app.route('/api/shipliyo/chatbot.xml', methods=['POST'])
def chatbot_xml():
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        session_id = data.get('session_id', 'default_session')
        
        if not message:
            return Response('''<?xml version="1.0" encoding="UTF-8"?>
<chatbot_response>
    <success>false</success>
    <message>Mesaj boş olamaz</message>
</chatbot_response>''', mimetype='application/xml'), 400
        
        from chatbot_manager import ChatbotManager
        chatbot = ChatbotManager()
        response = chatbot.handle_message(message, session_id, 'tr')
        
        # XML formatına çevir
        xml_response = f'''<?xml version="1.0" encoding="UTF-8"?>
<chatbot_response>
    <success>{str(response.get('success', False)).lower()}</success>
    <message><![CDATA[{response.get('response', '')}]]></message>
    <response_type>{response.get('response_type', 'direct')}</response_type>
</chatbot_response>'''
        
        return Response(xml_response, mimetype='application/xml')
        
    except Exception as e:
        return Response(f'''<?xml version="1.0" encoding="UTF-8"?>
<chatbot_response>
    <success>false</success>
    <message>API hatası: {str(e)}</message>
</chatbot_response>''', mimetype='application/xml'), 500

# Basit adres API'si (opsiyonel)
@app.route('/api/shipliyo/address')
def get_address():
    phone = request.args.get('phone', '')
    if len(phone) == 9 and phone.isdigit():
        return jsonify({
            "success": True,
            "address": f"BG{phone} Hatip Mahallesi Fulya Sokak No: 19/A Çorlu, Tekirdağ",
            "components": {
                "city": "Tekirdağ",
                "district": "Çorlu", 
                "neighborhood": "Hatip Mahallesi",
                "street": "Fulya Sokak", 
                "building": "19/A"
            }
        })
    else:
        return jsonify({
            "success": False, 
            "error": "Geçersiz telefon numarası. 9 haneli numara girin."
        }), 400

# ✅ WEB ARAYÜZÜ
@app.route('/')
def home():
    """Ana sayfa - web arayüzü"""
    return render_template('index.html')

# ✅ CHATBOT ENDPOINT'LERİ
@app.route('/api/chatbot', methods=['POST'])
def chatbot_handler():
    """Chatbot mesaj işleyici"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        session_id = data.get('session_id', 'default') 
        language = data.get('language', 'tr')
        
        print(f"CHATBOT REQUEST: '{message}'")
        print(f"Session: {session_id}, Language: {language}")
        
        response = chatbot.handle_message(message, session_id, language)
        
        print(f"CHATBOT RESPONSE: Success={response['success']}")
        print(f"Message: {response['response']}")
        print("-" * 50)
        
        return jsonify(response)
        
    except Exception as e:
        print(f"CHATBOT ERROR: {str(e)}")
        return jsonify({
            "success": False,
            "response": f"Hata oluştu: {str(e)}",
            "response_type": "direct"
        }), 500

@app.route('/api/languages', methods=['GET'])
def supported_languages():
    """Desteklenen dilleri listele"""
    return jsonify({
        "success": True,
        "languages": [
            {"code": "tr", "name": "Türkçe", "flag": "🇹🇷"},
            {"code": "bg", "name": "Bulgarca", "flag": "🇧🇬"},
            {"code": "en", "name": "İngilizce", "flag": "🇺🇸"}
        ]
    })

@app.route('/gateway-sms', methods=['POST'])
def gateway_sms():
    """Android app'in eski endpoint'i için yönlendirme"""
    try:
        data = request.get_json()
        from_number = data.get('from')
        body = data.get('body')
        device_id = data.get('deviceId', 'unknown')
        
        # ✅ DUPLICATE KONTROLÜ - Son 10 saniyedeki aynı SMS'leri kontrol et
        time_threshold = datetime.now() - timedelta(seconds=10)
        existing_sms = db.sms_messages.find_one({
            'from': from_number,
            'body': body,
            'timestamp': {'$gte': time_threshold}
        })
        
        if existing_sms:
            print(f"DUPLICATE SMS - Zaten kayıtlı: {existing_sms['_id']}")
            return jsonify({
                "status": "success", 
                "message": "SMS alındı (duplicate - zaten kayıtlı)",
                "sms_id": str(existing_sms['_id'])
            }), 200
        
        # ✅ YENİ SMS - Log'la ve kaydet
        print(f"YENİ SMS GELDİ - From: {from_number}")
        print(f"SMS İçeriği: {body}")
        print(f"Cihaz ID: {device_id}")
        print("-" * 50)
        
        sms_data = {
            'from': from_number,
            'body': body,
            'timestamp': datetime.now(),
            'device_id': device_id,
            'processed': False,
            'created_at': datetime.now(),
            'source': 'legacy_gateway'
        }
        
        result = db.sms_messages.insert_one(sms_data)
        print(f"MongoDB'ye kaydedildi - ID: {result.inserted_id}")
        
        return jsonify({
            "status": "success",
            "message": "SMS alındı (legacy endpoint)",
            "sms_id": str(result.inserted_id)
        }), 200
        
    except Exception as e:
        print(f"HATA: {str(e)}")
        return jsonify({
            "status": "error", 
            "message": f"Sistem hatası: {str(e)}"
        }), 500

@app.route('/incoming-sms', methods=['POST'])
def incoming_sms():
    """Yeni SMS endpoint'i"""
    try:
        data = request.get_json()
        
        # MongoDB'ye kaydet
        sms_data = {
            'from': data.get('from'),
            'body': data.get('body'),
            'timestamp': datetime.now(),
            'device_id': data.get('deviceId', 'unknown'),
            'processed': False,
            'created_at': datetime.now(),
            'source': 'new_gateway'
        }
        
        result = db.sms_messages.insert_one(sms_data)
        
        return jsonify({
            "status": "success",
            "message": "SMS alındı ve kaydedildi",
            "sms_id": str(result.inserted_id)
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Sistem hatası: {str(e)}"
        }), 500

@app.route('/api/sms', methods=['GET'])
def get_sms():
    """SMS'leri listeler (test için)"""
    try:
        sms_list = list(db.sms_messages.find().sort('timestamp', -1).limit(10))
        
        for sms in sms_list:
            sms['_id'] = str(sms['_id'])
            sms['timestamp'] = sms['timestamp'].isoformat() if sms.get('timestamp') else None
        
        return jsonify({
            "success": True,
            "count": len(sms_list),
            "sms_list": sms_list
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Backend sağlık kontrolü"""
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
        "version": "2.0.0"
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    print(f"Shipliyo Backend & Chatbot starting on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
