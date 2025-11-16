from flask import Flask, request, jsonify, Response, render_template
from flask_cors import CORS
from datetime import datetime, timedelta
import os

from dotenv import load_dotenv
load_dotenv()

from security.rate_limiter import rate_limiter
from security.validator import validator

app = Flask(__name__)
CORS(app)

MONGO_URI = os.getenv("MONGODB_URI")
if not MONGO_URI:
    raise ValueError("MONGODB_URI environment variable eksik!")

try:
    from pymongo import MongoClient
    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=10000,
        socketTimeoutMS=30000
        # ⬅️ SSL/TLS parametreleri YOK!
    )
    db = client.shipliyo_sms
    client.admin.command('ismaster')
    print("✅ MongoDB'ye BAĞLANDI")
except Exception as e:
    print(f"❌ MongoDB bağlantı hatası: {e}")
    client = None
    db = None

try:
    from chatbot_manager import ChatbotManager
    chatbot = ChatbotManager()
except Exception as e:
    print(f"❌ ChatbotManager yüklenemedi: {e}")
    chatbot = None

def get_client_identifier():
    return request.headers.get("X-Forwarded-For", request.remote_addr or "unknown")

def apply_rate_limits(max_per_minute=10, max_per_hour=100):
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

@app.before_request
def security_checks():
    if request.content_length and request.content_length > 1024 * 10:
        return jsonify({
            "success": False,
            "response": "İstek boyutu çok büyük",
            "response_type": "direct"
        }), 413
    
    if request.endpoint and request.method not in ["GET", "POST"]:
        return jsonify({
            "success": False,
            "response": "Geçersiz HTTP metodu",
            "response_type": "direct"
        }), 405

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/chatbot", methods=["POST"])
def chatbot_handler():
    # Rate limiting manual kontrol
    client_id = get_client_identifier()
    minute_key = f"minute_chatbot_{client_id}"
    if rate_limiter.is_rate_limited(minute_key, 10, 60):
        return jsonify({
            "success": False,
            "response": "Çok hızlı istek gönderiyorsunuz. Lütfen 1 dakika bekleyin.",
            "response_type": "direct"
        }), 429
    
    try:
        if not request.is_json:
            return jsonify({
                "success": False,
                "response": "JSON formatında veri gönderin",
                "response_type": "direct"
            }), 400
        
        data = request.get_json()
        message = data.get("message", "").strip()
        session_id = data.get("session_id", "default_session")
        language = data.get("language", "tr")
        
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

@app.route("/api/shipliyo/chatbot", methods=["POST"])
def shipliyo_chatbot_api():
    # Rate limiting manual kontrol
    client_id = get_client_identifier()
    minute_key = f"minute_shipliyo_chatbot_{client_id}"
    if rate_limiter.is_rate_limited(minute_key, 20, 60):
        return jsonify({
            "success": False,
            "response": "Çok hızlı istek gönderiyorsunuz. Lütfen 1 dakika bekleyin.",
            "response_type": "direct"
        }), 429
    try:
        if not request.is_json:
            return jsonify({
                "success": False,
                "response": "JSON formatında veri gönderin",
                "response_type": "direct"
            }), 400
        
        data = request.get_json()
        message = data.get("message", "").strip()
        session_id = data.get("session_id", "default_session")
        language = data.get("language", "tr")
        
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
                "response": "Chatbot servisi kullanılamıyor",
                "response_type": "direct"
            }), 503
        
        response = chatbot.handle_message(sanitized_msg, session_id, language)
        return jsonify(response)
        
    except Exception as e:
        print(f"❌ SHİPLİYO CHATBOT HATASI: {str(e)}")
        return jsonify({
            "success": False,
            "response": "API hatası oluştu",
            "response_type": "direct"
        }), 500

@app.route("/health", methods=["GET"])
def health_check():
    try:
        
        client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        
        if client:
            client.admin.command("ismaster")
            db_status = "connected"
        else:
            db_status = "disconnected"
        
        return jsonify({
            "status": "healthy",
            "service": "Shipliyo SMS Backend & Chatbot",
            "timestamp": datetime.now().isoformat(),
            "database": db_status,
            "railway_ip": client_ip,
            "version": "2.1.0"
        })
    except Exception as e:
        return jsonify({
            "status": "degraded",
            "service": "Shipliyo SMS Backend & Chatbot",
            "timestamp": datetime.now().isoformat(),
            "database": "disconnected",
            "error": str(e),
            "version": "2.1.0"
        }), 503

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print("🛡️  GÜVENLİ SHİPLİYO BACKEND BAŞLATILIYOR...")
    app.run(host="0.0.0.0", port=port, debug=False)