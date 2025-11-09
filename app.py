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
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
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

# ✅ ESKİ SMS ENDPOINT'LERİ (Aynen Koru)
@app.route('/gateway-sms', methods=['POST'])
def gateway_sms():
    # ... mevcut kodunuz aynen kalsın ...
    try:
        print("🎯 ESKİ ENDPOINT ÇAĞRILDI - /gateway-sms")
        data = request.get_json()
        # ... mevcut kod ...
        
@app.route('/incoming-sms', methods=['POST'])
def incoming_sms():
    # ... mevcut kodunuz aynen kalsın ...

@app.route('/api/sms', methods=['GET'])
def get_sms():
    # ... mevcut kodunuz aynen kalsın ...

@app.route('/api/search-sms', methods=['POST'])
def search_sms():
    # ... mevcut kodunuz aynen kalsın ...

@app.route('/health', methods=['GET'])
def health_check():
    # ... mevcut kodunuz aynen kalsın ...

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    print(f"🚀 Shipliyo Backend & Chatbot starting on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)