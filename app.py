from flask import Flask, request, jsonify, Response, render_template
from flask_cors import CORS
from datetime import datetime, timedelta
import os
import re
import psycopg2
from typing import Dict, Any

# Çevre değişkenlerini yükle
from dotenv import load_dotenv
load_dotenv()

# Güvenlik modülleri
from security.rate_limiter import rate_limiter
from security.validator import validator

app = Flask(__name__)
CORS(app)

# PostgreSQL bağlantısı
def get_db_connection():
    try:
        conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
        return conn
    except Exception as e:
        print(f"❌ PostgreSQL bağlantı hatası: {e}")
        return None

# Tabloları oluştur
def create_tables():
    try:
        conn = get_db_connection()
        if conn:
            cur = conn.cursor()
            # SMS mesajları tablosu
            cur.execute('''
                CREATE TABLE IF NOT EXISTS sms_messages (
                    id SERIAL PRIMARY KEY,
                    from_number TEXT NOT NULL,
                    body TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    device_id TEXT,
                    processed BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    source TEXT
                )
            ''')
            # Session tablosu (chatbot için)
            cur.execute('''
                CREATE TABLE IF NOT EXISTS chat_sessions (
                    id SERIAL PRIMARY KEY,
                    session_id TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
            cur.close()
            conn.close()
            print("✅ PostgreSQL tabloları oluşturuldu")
    except Exception as e:
        print(f"❌ Tablo oluşturma hatası: {e}")

# Uygulama başlangıcında tabloları oluştur
create_tables()

# Chatbot manager (geçici olarak MongoDB'siz çalışsın)
try:
    from chatbot_manager import ChatbotManager
    chatbot = ChatbotManager()
except Exception as e:
    print(f"❌ ChatbotManager yüklenemedi: {e}")
    chatbot = None

# ==================== GÜVENLİK FONKSİYONLARI ====================
def get_client_identifier() -> str:
    return request.headers.get('X-Forwarded-For', request.remote_addr or 'unknown')

def apply_rate_limits(max_per_minute: int = 10, max_per_hour: int = 100):
    def decorator(f):
        def wrapped(*args, **kwargs):
            client_id = get_client_identifier()
            endpoint_name = f.__name__
            
            minute_key = f"minute_{endpoint_name}_{client_id}"
            if rate_limiter.is_rate_limited(minute_key, max_per_minute, 60):
                return jsonify({
                    "success": False,
                    "response": "Çok hızlı istek gönderiyorsunuz. Lütfen 1 dakika bekleyin.",
                    "response_type": "direct"
                }), 429
            
            hour_key = f"hour_{endpoint_name}_{client_id}"
            if rate_limiter.is_rate_limited(hour_key, max_per_hour, 3600):
                return jsonify({
                    "success": False,
                    "response": "Günlük istek limitiniz doldu. Lütfen 1 saat bekleyin.",
                    "response_type": "direct"
                }), 429
            
            return f(*args, **kwargs)
        return wrapped
    return decorator

# ==================== ROUTE HANDLERS ====================
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/chatbot', methods=['POST'])
@apply_rate_limits(max_per_minute=10, max_per_hour=200)
def chatbot_handler():
    try:
        if not request.is_json:
            return jsonify({
                "success": False,
                "response": "JSON formatında veri gönderin",
                "response_type": "direct"
            }), 400
        
        data = request.get_json()
        message = data.get('message', '').strip()
        session_id = data.get('session_id', 'default_session')
        language = data.get('language', 'tr')
        
        is_valid_msg, sanitized_msg = validator.sanitize_message(message)
        if not is_valid_msg:
            return jsonify({
                "success": False,
                "response": sanitized_msg or "Geçersiz mesaj",
                "response_type": "direct"
            }), 400
        
        if not chatbot:
            return jsonify({
                "success": False,
                "response": "Chatbot servisi şu anda kullanılamıyor",
                "response_type": "direct"
            }), 503
        
        response = chatbot.handle_message(sanitized_msg, session_id, language)
        return jsonify(response)
        
    except Exception as e:
        print(f"❌ CHATBOT HATASI: {str(e)}")
        return jsonify({
            "success": False,
            "response": "Sistem hatası oluştu",
            "response_type": "direct"
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    try:
        client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        conn = get_db_connection()
        
        if conn:
            conn.close()
            db_status = "connected"
        else:
            db_status = "disconnected"
        
        return jsonify({
            "status": "healthy",
            "service": "Shipliyo SMS Backend & Chatbot",
            "timestamp": datetime.now().isoformat(),
            "database": db_status,
            "railway_ip": client_ip,
            "version": "2.2.0",
            "database_type": "PostgreSQL"
        })
    except Exception as e:
        return jsonify({
            "status": "degraded",
            "service": "Shipliyo SMS Backend & Chatbot",
            "timestamp": datetime.now().isoformat(),
            "database": "disconnected", 
            "error": str(e),
            "version": "2.2.0"
        }), 503


@app.route('/gateway-sms', methods=['POST'])
# @apply_rate_limits(max_per_minute=30, max_per_hour=300)  # 🚨 GEÇİCİ OLARAK KALDIRILDI
def gateway_sms():
    try:
        if not request.is_json:
            return jsonify({"error": "JSON formatında veri gönderin"}), 400
        
        data = request.get_json()
        print(f"📨 SMS Alındı: {data}")
        
        # Gerekli alanları kontrol et
        from_number = data.get('from', '').strip()
        body = data.get('body', '').strip()
        device_id = data.get('deviceId', 'android_gateway')
        
        if not from_number or not body:
            return jsonify({"error": "from ve body alanları zorunludur"}), 400
        
        # ✅ 1. PostgreSQL'e kaydet
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database bağlantı hatası"}), 500
            
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO sms_messages 
            (from_number, body, device_id, processed, source, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (from_number, body, device_id, False, 'android_gateway', datetime.now()))
        conn.commit()
        
        # ✅ 2. Chatbot'u HEMEN tetikle
        if chatbot:
            try:
                # SMS'i chatbot'a işlet
                chatbot_response = chatbot.handle_message(body, from_number, 'tr')
                print(f"🤖 Chatbot Yanıtı: {chatbot_response}")
                
                # İsteğe bağlı: Yanıtı başka bir tabloya kaydedebilirsiniz
                cur.execute('''
                    INSERT INTO chatbot_responses 
                    (from_number, user_message, bot_response, timestamp)
                    VALUES (%s, %s, %s, %s)
                ''', (from_number, body, chatbot_response.get('response', ''), datetime.now()))
                conn.commit()
                
            except Exception as e:
                print(f"⚠️ Chatbot işleme hatası: {e}")
        
        cur.close()
        conn.close()
        
        print(f"✅ SMS başarıyla işlendi: {from_number}")
        return jsonify({
            "status": "success",
            "message": "SMS başarıyla alındı ve işlendi",
            "processed": True
        })
        
    except Exception as e:
        print(f"❌ GATEWAY-SMS HATASI: {str(e)}")
        return jsonify({"error": f"Sistem hatası: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    print("🔄 PostgreSQL ile Shipliyo Backend başlatılıyor...")
    app.run(host='0.0.0.0', port=port, debug=False)