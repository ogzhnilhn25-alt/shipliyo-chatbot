from flask import Flask, request, jsonify, Response, render_template
from flask_cors import CORS
from datetime import datetime, timedelta
import time
import json
import os
import re
import psycopg2
from psycopg2 import OperationalError
from collections import defaultdict
from dotenv import load_dotenv

# Flask uygulamasını en başta tanımlıyoruz (Hata riskini sıfıra indirmek için)
app = Flask(__name__)
CORS(app, origins=["*"])
load_dotenv()

# --- GÜVENLİK MODÜLLERİ ---
try:
    from security.rate_limiter import rate_limiter
    from security.validator import validator
except ImportError:
    class DummyValidator:
        def sanitize_message(self, msg): return True, msg
    validator = DummyValidator()
    print("⚠️ UYARI: Security modülleri bulunamadı, varsayılanlar kullanılıyor.")
except Exception as e:
    print(f"⚠️ Kritik Import Hatası: {e}")
    # Uygulamanın çökmesini engellemek için dummy oluştur
    class DummyValidator:
        def sanitize_message(self, msg): return True, msg
    validator = DummyValidator()

# --- VERİTABANI BAĞLANTISI ---
def get_db_connection():
    db_url = os.environ.get('DATABASE_PRIVATE_URL')
    
    if not db_url and os.environ.get('PGHOST'):
         try:
            db_url = f"postgres://{os.environ.get('PGUSER')}:{os.environ.get('PGPASSWORD')}@{os.environ.get('PGHOST')}:{os.environ.get('PGPORT')}/{os.environ.get('PGDATABASE')}"
         except: pass
    
    if not db_url:
        db_url = os.environ.get('DATABASE_URL')

    if not db_url:
        print("❌ HATA: DB URL bulunamadı.")
        return None

    if "sslmode" not in db_url:
        if "?" in db_url:
            db_url += "&sslmode=require"
        else:
            db_url += "?sslmode=require"

    try:
        conn = psycopg2.connect(db_url, connect_timeout=10)
        return conn
    except Exception as e:
        print(f"❌ Veritabanı Bağlantı Hatası: {e}")
        return None

# --- TABLO OLUŞTURMA ---
def create_tables():
    print("\n🔍 --- BAŞLANGIÇ KONTROLÜ ---")
    keys = [k for k in os.environ.keys() if 'PG' in k or 'DB' in k or 'DATABASE' in k]
    for k in keys:
        val = os.environ[k]
        hint = "✅ Private/Internal"
        if "ballast" in val: hint = "⚠️ PUBLIC PROXY (Sorunlu)"
        print(f"   🔑 {k}: [{hint}]")
    print("------------------------------\n")

    conn = get_db_connection()
    if not conn:
        print("❌ Tablolar oluşturulamadı: Bağlantı yok.")
        return

    try:
        cur = conn.cursor()
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

# Uygulama başlarken tabloları kontrol et
try:
    create_tables()
except Exception as e:
    print(f"⚠️ Tablo oluşturma sırasında hata (Kritik Değil): {e}")

# --- YARDIMCI FONKSİYONLAR ---
sms_duplicate_cache = {}
SMS_CACHE_TIMEOUT = 5

def check_sms_duplicate(from_number, body, timestamp):
    current_time = time.time()
    duplicate_key = f"{from_number}_{body}_{timestamp}"
    
    if duplicate_key in sms_duplicate_cache:
        cache_time = sms_duplicate_cache[duplicate_key]
        if current_time - cache_time < SMS_CACHE_TIMEOUT:
            print(f"🔄 DUPLICATE SMS ENGELLENDİ: {duplicate_key}")
            return True
    
    sms_duplicate_cache[duplicate_key] = current_time
    for key in list(sms_duplicate_cache.keys()):
        if current_time - sms_duplicate_cache[key] > 60:
            del sms_duplicate_cache[key]
    return False

rate_limit_data = defaultdict(list)

def check_rate_limit(client_ip, max_requests=30, window_seconds=60):
    current_time = time.time()
    rate_limit_data[client_ip] = [
        req_time for req_time in rate_limit_data[client_ip] 
        if current_time - req_time < window_seconds
    ]
    if len(rate_limit_data[client_ip]) >= max_requests:
        return False, window_seconds
    rate_limit_data[client_ip].append(current_time)
    return True, 0

def validate_phone_number(phone):
    if not phone: return False
    pattern = r'^\+?[1-9]\d{1,14}$'
    return re.match(pattern, phone) is not None

def validate_message_content(message):
    if not message or len(message.strip()) == 0:
        return False, "Boş mesaj gönderilemez"
    if len(message) > 1000:
        return False, "Mesaj çok uzun (max 1000 karakter)"
    return True, ""

def verify_user_agent():
    user_agent = request.headers.get('User-Agent', '')
    allowed_agents = ['Shipliyo-SMS-Gateway', 'Android', 'Dalvik']
    for allowed in allowed_agents:
        if allowed in user_agent:
            return True
    print(f"🚫 Yetkisiz User-Agent: {user_agent}")
    return False

# --- ROUTE HANDLERS ---
@app.route('/')
def home():
    try:
        return render_template('index.html')
    except Exception as e:
        return f"<h3>Arayüz Yüklenemedi</h3><p>Hata: {e}</p><p>Lütfen 'templates/index.html' dosyasının var olduğundan emin olun.</p>"

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
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr or 'unknown')
    allowed, retry_after = check_rate_limit(client_ip, 60, 60)
    if not allowed:
        return jsonify({"error": f"Hız sınırı aşıldı. {retry_after}sn bekleyin."}), 429

    if not verify_user_agent(): return jsonify({"error": "Yetkisiz erişim"}), 403
    if not request.is_json: return jsonify({"error": "JSON gerekli"}), 400

    try:
        data = request.get_json()
        print(f"📨 SMS GELDİ: {data}")

        from_number = data.get('from', '').strip()
        body = data.get('body', '').strip()
        timestamp = data.get('timestamp', '')
        device_id = data.get('deviceId', 'android_gateway')

        if check_sms_duplicate(from_number, body, timestamp):
            return jsonify({"status": "duplicate", "message": "Zaten işlendi"}), 200

        is_valid_msg, msg_error = validate_message_content(body)
        if not is_valid_msg: return jsonify({"error": msg_error}), 400

        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Veritabanı bağlantısı kurulamadı"}), 500

        try:
            cur = conn.cursor()
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

            try:
                from chatbot_manager import ChatbotManager
                temp_chatbot = ChatbotManager()
                bot_response = temp_chatbot.handle_message(body, from_number, 'tr')
                print(f"🤖 Chatbot Yanıtı: {bot_response}")
            except Exception as e:
                print(f"⚠️ Chatbot Hatası: {e}")
            
            return jsonify({
                "status": "success",
                "message": "SMS işlendi",
                "processed": True
            })

        finally:
            if conn: conn.close()

    except Exception as e:
        print(f"❌ GATEWAY HATASI: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/chatbot', methods=['POST'])
def chatbot_api():
    try:
        from chatbot_manager import ChatbotManager
        temp_chatbot = ChatbotManager()
        
        data = request.get_json()
        msg = data.get('message', '')
        session_id = data.get('session_id', 'web-user')
        
        response = temp_chatbot.handle_message(msg, session_id, 'tr')
        return jsonify(response)
    except Exception as e:
        print(f"❌ API Chatbot Hatası: {e}")
        return jsonify({"error": "İşlem başarısız"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    print(f"🚀 Sunucu {port} portunda başlatılıyor...")
    app.run(host='0.0.0.0', port=port, debug=False)