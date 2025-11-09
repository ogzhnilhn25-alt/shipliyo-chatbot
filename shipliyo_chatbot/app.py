import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import uuid
from datetime import datetime
from chatbot_manager import ChatbotManager

app = Flask(__name__)

# Production CORS settings
CORS(app)

# Initialize chatbot
chatbot = ChatbotManager()

@app.route('/')
def home():
    return jsonify({
        "status": "Shipliyo Chatbot API", 
        "version": "1.0.0",
        "message": "API is running successfully!"
    })


@app.route('/')
def chat_interface():
    """Chatbot web arayüzü"""
    return render_template('index.html')

@app.route('/api/chatbot', methods=['POST'])
def chatbot_endpoint():
    """
    Ana chatbot endpoint'i
    Çok dilli destek: tr, bg, en
    """
    try:
        data = request.get_json()
        
        # Boş mesajsa ana menü göster
        if not data or 'message' not in data or not data.get('message', '').strip():
            response = chatbot._handle_main_menu(data.get('language', 'tr') if data else 'tr')
            response['session_id'] = str(uuid.uuid4())
            response['timestamp'] = datetime.now().isoformat()
            return jsonify(response)
        
        # Gerekli alanları kontrol et
        message = data.get('message', '').strip()
        session_id = data.get('session_id', str(uuid.uuid4()))
        language = data.get('language', 'tr')  # Varsayılan: Türkçe
        
        if not message:
            return jsonify({
                "success": False,
                "error": "Mesaj boş olamaz"
            }), 400
        
        # Language validation
        if language not in ['tr', 'bg', 'en']:
            language = 'tr'
        
        # Chatbot'a yönlendir
        response = chatbot.handle_message(message, session_id, language)
        
        # Session ID'yi response'a ekle
        response['session_id'] = session_id
        response['timestamp'] = datetime.now().isoformat()
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Sistem hatası: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/site-selection', methods=['POST'])
def site_selection():
    """
    Site seçiminden sonra son SMS'leri getir
    """
    try:
        data = request.get_json()
        
        session_id = data.get('session_id', '')
        site = data.get('site', '')
        language = data.get('language', 'tr')
        seconds = data.get('seconds', 90)  # Varsayılan: 90 saniye
        
        if not site:
            return jsonify({
                "success": False,
                "error": "Site seçimi gereklidir"
            }), 400
        
        # Son SMS'leri getir
        response = chatbot.get_recent_sms_by_site(site, seconds, language)
        response['session_id'] = session_id
        response['timestamp'] = datetime.now().isoformat()
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Sistem hatası: {str(e)}"
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Sistem sağlık kontrolü"""
    return jsonify({
        "status": "healthy",
        "service": "Shipliyo Chatbot API",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "features": [
            "Çok dilli destek (tr, bg, en)",
            "Referans kodu arama", 
            "Site bazlı SMS listeleme",
            "Real-time SMS işleme",
            "Baloncuk menü sistemi",
            "Web arayüzü"
        ]
    })

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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))  # Railway PORT değişkenini kullan
    print("🚀 Shipliyo Chatbot API başlatılıyor...")
    print(f"📍 Port: {port}")
    print("🌐 Web Arayüzü: http://localhost:" + str(port))
    print("🌍 Desteklenen diller: Türkçe, Bulgarca, İngilizce")
    print("📱 Özellikler: Referans kodu arama, Site seçimi, Çok dilli, Baloncuk menü")
    print("─" * 60)
    
    app.run(host='0.0.0.0', port=port, debug=False)  # Production'da debug=False