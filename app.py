from flask import Flask, request, jsonify, Response, render_template
from flask_cors import CORS
from datetime import datetime, timedelta
import base64
import time
import json
import os
import re
import psycopg2
from psycopg2 import OperationalError # Hata yakalamak için gerekli
from typing import Dict, Any
from collections import defaultdict

# Çevre değişkenlerini yükle
from dotenv import load_dotenv
load_dotenv()

# Güvenlik modülleri (varsa)
try:
    from security.rate_limiter import rate_limiter
    from security.validator import validator
except ImportError:
    # Eğer bu dosyalar yoksa kod patlamasın diye dummy classlar
    class DummyValidator:
        def sanitize_message(self, msg): return True, msg
    validator = DummyValidator()
    print("⚠️ UYARI: Security modülleri bulunamadı, varsayılanlar kullanılıyor.")

# ==================== DUPLICATE PROTECTION ====================
sms_duplicate_cache = {}
SMS_CACHE_TIMEOUT = 5  # 5 saniye

def check_sms_duplicate(from_number, body, timestamp):
    """Aynı SMS'in kısa sürede tekrar gelmesini engelle"""
    current_time = time.time()
    duplicate_key = f"{from_number}_{body}_{timestamp}"
    
    if duplicate_key in sms_duplicate_cache:
        cache_time = sms_duplicate_cache[duplicate_key]
        if current_time - cache_time < SMS_CACHE_TIMEOUT:
            print(f"🔄 DUPLICATE SMS ENGELLENDİ: {duplicate_key}")
            return True
    
    sms_duplicate_cache[duplicate_key] = current_time
    
    # Temizlik (Garbage Collection)
    for key in list(sms_duplicate_cache.keys()):
        if current_time - sms_duplicate_cache[key] > 60:
            del sms_duplicate_cache[key]
    
    return False

# ==================== RATE LIMITING & VALIDATIONS ====================
rate_limit_data = defaultdict(list)

def check_rate_limit(client_ip, max_requests=30, window_seconds=60):
    """Basit IP bazlı rate limiting"""
    current_time = time.time()
    # Eski kayıtları temizle
    rate_limit_data[client_ip] = [
        req_time for req_time in rate_limit_data[client_ip] 
        if current_time - req_time < window_seconds
    ]
    
    if len(rate_limit_data[client_ip]) >= max_requests:
        return False, window_seconds
    
    rate_limit_data[client_ip].append(current_time)
    return True, 0

def validate_phone_number(phone):
    """Telefon numarası validasyonu"""
    if not phone: return False
    pattern = r'^\+?[1-9]\d{1,14}$'
    return re.match(pattern, phone) is not None

def validate_message_content(message):
    """Mesaj içeriği validasyonu"""
    if not message or len(message.strip()) == 0:
        return False, "Boş mesaj gönderilemez"
    if len(message) > 1000:
        return False, "Mesaj çok uzun (max 1000 karakter)"
    return True, ""

def verify_user_agent():
    """User-Agent doğrulama"""
    user_agent = request.headers.get('User-Agent', '')
    allowed_agents = ['Shipliyo-SMS-Gateway', 'Android', 'Dalvik']
    for allowed in allowed_agents:
        if allowed in user_agent:
            return True
    print(f"🚫 Yetkisiz User-Agent: {user_agent}")
    return False

# ==================== FLASK APP SETUP ====================
app = Flask(__name__)
CORS(app, origins=["*"]) # Tüm kaynaklara izin ver (Production'da daraltılabilir)

# ==================== DB CONNECTION (ARMORED VERSION) ====================
def get_db_connection():
    """
    Railway Public Proxy (ballast) kopmalarına karşı dirençli bağlantı fonksiyonu.
    Retry mekanizması ve Keepalive ayarları içerir.
    """
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print("❌ DATABASE_URL bulunamadı!")
        return None

    max_retries = 3
    for attempt in range(max_retries):
        try:
            conn = psycopg2.connect(
                db_url,
                keepalives=1,           # Bağlantıyı canlı tut
                keepalives_idle=30,     # 30 sn boşta kalırsa kontrol et
                keepalives_interval=10, # 10 saniyede bir sinyal at
                keepalives_count=5,     # 5 kere cevap gelmezse kopar
                connect_timeout=10      # 10 saniyede bağlanamazsa pes et
            )
            return conn
        except OperationalError as e:
            print(f"⚠️ Bağlantı hatası (Deneme {attempt+1}/{max_retries}): {e}")
            time.sleep(1) # Biraz bekle tekrar dene
        except Exception as e:
            print(f"❌ Kritik DB Hatası: {e}")
            return None
    
    print("❌ Veritabanına bağlanılamadı (Tüm denemeler başarısız).")
    return None

# ==================== TABLE CREATION ====================
def create_tables():
    conn = get_db_connection()
    if not conn:
        print("❌ Tablolar oluşturulamadı: Bağlantı yok.")
        return

    try:
        cur = conn.cursor()
        # SMS Tablosu
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
        # Session Tablosu
        cur.execute('''
            CREATE TABLE IF NOT EXISTS chat_sessions (
                id SERIAL PRIMARY KEY,
                session_id TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        print("✅ PostgreSQL tabloları hazır.")
    except Exception as e:
        print(f"❌ Tablo oluşturma hatası: {e}")
    finally:
        if conn: conn.close()

# Başlangıçta tabloları kontrol et
create_tables()

# ==================== CHATBOT MANAGER ====================
# Global instance'ı sadece web API için tutuyoruz.
# SMS Gateway için taze instance kullanacağız.
try:
    from chatbot_manager import ChatbotManager
    global_chatbot = ChatbotManager()
except Exception as e:
    print(f"❌ ChatbotManager yüklenemedi: {e}")
    global_chatbot = None

# ==================== ROUTE HANDLERS ====================
@app.route('/')
def home():
    return "Shipliyo SMS Backend is Running 🚀"

@app.route('/health', methods=['GET'])
def health_check():
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    conn = get_db_connection()
    db_status = "connected" if conn else "disconnected"
    if conn: conn.close()
    
    return jsonify({
        "status": "healthy" if db_status == "connected" else "degraded",
        "service": "Shipliyo SMS Backend",
        "database": db_status,
        "ip": client_ip,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/gateway-sms', methods=['POST'])
def gateway_sms():
    # 1. Rate Limit
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr or 'unknown')
    allowed, retry_after = check_rate_limit(client_ip, 60, 60) # Dakikada 60 SMS
    if not allowed:
        return jsonify({"error": f"Hız sınırı aşıldı. {retry_after}sn bekleyin."}), 429

    # 2. Güvenlik Kontrolleri
    if not verify_user_agent(): return jsonify({"error": "Yetkisiz erişim"}), 403
    if not request.is_json: return jsonify({"error": "JSON gerekli"}), 400

    try:
        data = request.get_json()
        print(f"📨 SMS GELDİ: {data}")

        from_number = data.get('from', '').strip()
        body = data.get('body', '').strip()
        timestamp = data.get('timestamp', '')
        device_id = data.get('deviceId', 'android_gateway')

        # 3. Duplicate Check
        if check_sms_duplicate(from_number, body, timestamp):
            return jsonify({"status": "duplicate", "message": "Zaten işlendi"}), 200

        # 4. Validasyonlar
        is_valid_msg, msg_error = validate_message_content(body)
        if not is_valid_msg: return jsonify({"error": msg_error}), 400

        # 5. DB Kaydı
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Veritabanı bağlantısı kurulamadı"}), 500

        try:
            cur = conn.cursor()
            # Timestamp düzeltme
            try:
                sms_ts = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except:
                sms_ts = datetime.now()

            cur.execute('''
                INSERT INTO sms_messages 
                (from_number, body, device_id, processed, source, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (from_number, body, device_id, False, 'android_gateway', sms_ts))
            
            conn.commit()
            cur.close()
            print(f"✅ SMS DB'ye Yazıldı: {from_number}")

            # 6. Chatbot Tetikleme (TAZE BAĞLANTI İLE)
            # Burada global instance yerine taze import yapıyoruz ki 
            # eski connection hatası vermesin.
            try:
                # Eğer ChatbotManager modül olarak import edildiyse:
                from chatbot_manager import ChatbotManager
                # Taze instance oluştur
                temp_chatbot = ChatbotManager()
                # İşlemi yap
                bot_response = temp_chatbot.handle_message(body, from_number, 'tr')
                print(f"🤖 Chatbot Yanıtı: {bot_response}")
            except Exception as e:
                print(f"⚠️ Chatbot Hatası (Kritik değil): {e}")
                # Chatbot hatası SMS alımını başarısız göstermemeli
            
            return jsonify({
                "status": "success",
                "message": "SMS işlendi",
                "processed": True
            })

        finally:
            # Ne olursa olsun bağlantıyı kapat
            if conn: conn.close()

    except Exception as e:
        print(f"❌ GATEWAY HATASI: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/chatbot', methods=['POST'])
def chatbot_api():
    """Web arayüzü için chatbot endpoint'i"""
    if not global_chatbot:
        return jsonify({"error": "Servis kullanılamıyor"}), 503
    
    data = request.get_json()
    msg = data.get('message', '')
    session_id = data.get('session_id', 'web-user')
    
    try:
        response = global_chatbot.handle_message(msg, session_id, 'tr')
        return jsonify(response)
    except Exception as e:
        print(f"❌ API Chatbot Hatası: {e}")
        return jsonify({"error": "İşlem başarısız"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    print(f"🚀 Sunucu {port} portunda başlatılıyor...")
    app.run(host='0.0.0.0', port=port, debug=False)