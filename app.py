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

from collections import defaultdict
import time

# ==================== DUPLICATE PROTECTION ====================
# SMS duplicate koruması için cache
sms_duplicate_cache = {}
SMS_CACHE_TIMEOUT = 5  # 5 saniye

def check_sms_duplicate(from_number, body, timestamp):
    """Aynı SMS'in kısa sürede tekrar gelmesini engelle"""
    current_time = time.time()
    
    # Duplicate key oluştur
    duplicate_key = f"{from_number}_{body}_{timestamp}"
    
    # Cache'te var mı kontrol et
    if duplicate_key in sms_duplicate_cache:
        cache_time = sms_duplicate_cache[duplicate_key]
        if current_time - cache_time < SMS_CACHE_TIMEOUT:
            print(f"🔄 DUPLICATE SMS ENGELlENDİ: {duplicate_key}")
            return True
    
    # Cache'e kaydet
    sms_duplicate_cache[duplicate_key] = current_time
    
    # Eski cache'leri temizle (1 dakikadan eski)
    for key in list(sms_duplicate_cache.keys()):
        if current_time - sms_duplicate_cache[key] > 60:
            del sms_duplicate_cache[key]
    
    return False

# Basit in-memory rate limiting
request_history = defaultdict(list)

def simple_rate_limit(max_requests=30, window_seconds=60):
    """Basit IP bazlı rate limiting"""
    def decorator(f):
        def wrapped(*args, **kwargs):
            client_ip = request.headers.get('X-Forwarded-For', request.remote_addr or 'unknown')
            current_time = time.time()
            
            # Eski kayıtları temizle
            request_history[client_ip] = [
                req_time for req_time in request_history[client_ip] 
                if current_time - req_time < window_seconds
            ]
            
            # Rate limit kontrolü
            if len(request_history[client_ip]) >= max_requests:
                print(f"🚫 Rate limit aşıldı: {client_ip}")
                return jsonify({
                    "error": "Çok fazla istek gönderiyorsunuz. Lütfen 1 dakika bekleyin.",
                    "retry_after": window_seconds
                }), 429
            
            # İsteği kaydet
            request_history[client_ip].append(current_time)
            return f(*args, **kwargs)
        return wrapped
    return decorator

def validate_phone_number(phone):
    """Telefon numarası validasyonu"""
    if not phone:
        return False
    # Uluslararası format: +905551234567 veya 905551234567
    pattern = r'^\+?[1-9]\d{1,14}$'
    return re.match(pattern, phone) is not None

def validate_message_content(message):
    """Mesaj içeriği validasyonu"""
    if not message or len(message.strip()) == 0:
        return False, "Boş mesaj gönderilemez"
    
    if len(message) > 1000:
        return False, "Mesaj çok uzun (max 1000 karakter)"
    
    # Kötü niyetli içerik kontrolü (basit)
    blocked_patterns = [
        r'(.)\1{10,}',  # Aynı karakterin 10+ tekrarı
        r'http[s]?://', # URL'ler
    ]
    
    for pattern in blocked_patterns:
        if re.search(pattern, message, re.IGNORECASE):
            return False, "Geçersiz mesaj içeriği"
    
    return True, ""

def verify_user_agent():
    """User-Agent doğrulama - Sadece Android uygulamamız"""
    user_agent = request.headers.get('User-Agent', '')
    allowed_agents = ['Shipliyo-SMS-Gateway', 'Android', 'Dalvik']
    
    for allowed in allowed_agents:
        if allowed in user_agent:
            return True
    
    print(f"🚫 Yetkisiz User-Agent: {user_agent}")
    return False

from collections import defaultdict
import time

# ==================== GÜVENLİK FONKSİYONLARI ====================
# Rate limiting storage
rate_limit_data = defaultdict(list)

def check_rate_limit(client_ip, max_requests=30, window_seconds=60):
    """Fonksiyon içinde kullanılacak rate limiting"""
    current_time = time.time()
    
    # Eski kayıtları temizle
    rate_limit_data[client_ip] = [
        req_time for req_time in rate_limit_data[client_ip] 
        if current_time - req_time < window_seconds
    ]
    
    # Rate limit kontrolü
    if len(rate_limit_data[client_ip]) >= max_requests:
        return False, window_seconds
    
    # İsteği kaydet
    rate_limit_data[client_ip].append(current_time)
    return True, 0

app = Flask(__name__)
CORS(app, origins=[
    "https://www.shipliyo.com",
    "https://shipliyo.com",
    "http://localhost:3000",
    "https://shipliyo-chatbot-production.up.railway.app"
])

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
def gateway_sms():
    # ✅ 1. RATE LİMİT KONTROLÜ
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr or 'unknown')
    is_allowed, retry_after = check_rate_limit(client_ip, 30, 60)
    
    if not is_allowed:
        print(f"🚫 Rate limit aşıldı: {client_ip}")
        return jsonify({
            "error": f"Çok fazla istek gönderiyorsunuz. Lütfen {retry_after} saniye bekleyin."
        }), 429
    
    # ✅ 2. User-Agent Doğrulama
    if not verify_user_agent():
        return jsonify({"error": "Yetkisiz erişim"}), 403
    
    # ✅ 3. JSON Format Kontrolü
    if not request.is_json:
        return jsonify({"error": "JSON formatında veri gönderin"}), 400
    
    # ✅ 4. Request Boyut Kontrolü
    if request.content_length > 1024 * 10:  # 10KB
        return jsonify({"error": "İstek boyutu çok büyük"}), 413
    
    # ✅ TRY BLOĞU EKLEYİN (BU EKSİK!)
    try:
        data = request.get_json()
        client_ip = request.headers.get('X-Forwarded-For', request.remote_addr or 'unknown')
        
        # ✅ 5. DUPLICATE SMS KONTROLÜ (YENİ EKLENDİ)
        from_number = data.get('from', '').strip()
        body = data.get('body', '').strip()
        timestamp = data.get('timestamp', '')
        
        # Duplicate kontrolü yap
        if check_sms_duplicate(from_number, body, timestamp):
            return jsonify({
                "status": "duplicate", 
                "message": "SMS zaten işlendi"
            }), 200
        
        print(f"📨 SMS Alındı - IP: {client_ip}, Data: {data}")
        
        # ✅ 6. Giriş Validasyonu
        device_id = data.get('deviceId', 'android_gateway')
        
        # Telefon numarası validasyonu
        if not validate_phone_number(from_number):
            return jsonify({"error": "Geçersiz telefon numarası formatı"}), 400
        
        # Mesaj içeriği validasyonu
        is_valid_msg, msg_error = validate_message_content(body)
        if not is_valid_msg:
            return jsonify({"error": msg_error}), 400
        
        # Device ID validasyonu
        if device_id and len(device_id) > 100:
            return jsonify({"error": "Geçersiz cihaz ID"}), 400
        
        # ✅ 7. PostgreSQL'e kaydet
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
        
        # ✅ 8. Chatbot'u tetikle
        if chatbot:
            try:
                chatbot_response = chatbot.handle_message(body, from_number, 'tr')
                print(f"🤖 Chatbot Yanıtı: {chatbot_response}")
                
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
        
    except Exception as e:  # 🎯 ARTIK TRY BLOĞU VAR!
        print(f"❌ GATEWAY-SMS HATASI: {str(e)}")
        return jsonify({"error": f"Sistem hatası: {str(e)}"}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    print("🔄 PostgreSQL ile Shipliyo Backend başlatılıyor...")
    app.run(host='0.0.0.0', port=port, debug=False)