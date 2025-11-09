from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime
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
        
        response = chatbot.handle_message(message, session_id, language)
        return jsonify(response)
        
    except Exception as e:
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

# ✅ ESKİ SMS ENDPOINT'LERİ
@app.route('/gateway-sms', methods=['POST'])
def gateway_sms():
    """Android app'in eski endpoint'i için yönlendirme"""
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
            'source': 'legacy_gateway'
        }
        
        result = db.sms_messages.insert_one(sms_data)
        
        return jsonify({
            "status": "success",
            "message": "SMS alındı (legacy endpoint)",
            "sms_id": str(result.inserted_id)
        }), 200
        
    except Exception as e:
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
    print(f"🚀 Shipliyo Backend & Chatbot starting on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)