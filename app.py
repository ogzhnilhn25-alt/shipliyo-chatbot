from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

# Çevre değişkenlerini yükle
load_dotenv()

app = Flask(__name__)
CORS(app)

# MongoDB bağlantısı
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
client = MongoClient(MONGO_URI)
db = client.shipliyo_sms

@app.route('/gateway-sms', methods=['POST'])
def gateway_sms():
    """
    Android app'in eski endpoint'i için yönlendirme
    """
    try:
        print("🎯 ESKİ ENDPOINT ÇAĞRILDI - /gateway-sms")
        
        # Gelen veriyi al
        data = request.get_json()
        
        print(f"📱 Gönderen: {data.get('from', 'Bilinmeyen')}")
        print(f"💬 Mesaj: {data.get('body', 'Boş')}")
        print(f"⏰ Zaman: {datetime.now()}")
        
        # MongoDB'ye kaydet
        sms_data = {
            'from': data.get('from'),
            'body': data.get('body'),
            'timestamp': datetime.now(),
            'device_id': data.get('deviceId', 'unknown'),
            'processed': False,
            'created_at': datetime.now(),
            'source': 'legacy_gateway'  # Kaynak bilgisi
        }
        
        result = db.sms_messages.insert_one(sms_data)
        
        print(f"✅ MongoDB'ye kaydedildi: {result.inserted_id}")
        
        return jsonify({
            "status": "success",
            "message": "SMS alındı (legacy endpoint)",
            "sms_id": str(result.inserted_id)
        }), 200
        
    except Exception as e:
        print(f"❌ HATA: {str(e)}")
        return jsonify({
            "status": "error", 
            "message": f"Sistem hatası: {str(e)}"
        }), 500

@app.route('/incoming-sms', methods=['POST'])
def incoming_sms():
    """
    Yeni SMS endpoint'i
    """
    try:
        data = request.get_json()
        
        print("🎉🎉🎉 YENİ SMS GELDİ! 🎉🎉🎉")
        print(f"📱 Gönderen: {data.get('from', 'Bilinmeyen')}")
        print(f"💬 Mesaj: {data.get('body', 'Boş')}")
        print(f"⏰ Zaman: {data.get('timestamp', 'Bilinmeyen')}")
        
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
        
        print(f"✅ MongoDB'ye kaydedildi: {result.inserted_id}")
        
        return jsonify({
            "status": "success",
            "message": "SMS alındı ve kaydedildi",
            "sms_id": str(result.inserted_id)
        }), 200
        
    except Exception as e:
        print(f"❌ HATA: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Sistem hatası: {str(e)}"
        }), 500

@app.route('/api/sms', methods=['GET'])
def get_sms():
    """
    SMS'leri listeler (test için)
    """
    try:
        # Son 10 SMS'i getir
        sms_list = list(db.sms_messages.find().sort('timestamp', -1).limit(10))
        
        # ObjectId'yi string'e çevir
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

@app.route('/api/search-sms', methods=['POST'])
def search_sms():
    """
    Referans kodu veya içerikle SMS ara
    """
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({
                "success": False,
                "error": "Arama sorgusu gereklidir"
            }), 400
        
        # MongoDB'de ara
        search_filter = {
            '$or': [
                {'body': {'$regex': query, '$options': 'i'}},
                {'from': {'$regex': query, '$options': 'i'}}
            ]
        }
        
        results = list(db.sms_messages.find(search_filter).sort('timestamp', -1).limit(5))
        
        # ObjectId'yi string'e çevir
        for sms in results:
            sms['_id'] = str(sms['_id'])
            sms['timestamp'] = sms['timestamp'].isoformat() if sms.get('timestamp') else None
        
        return jsonify({
            "success": True,
            "count": len(results),
            "results": results
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
        # MongoDB bağlantısını test et
        client.admin.command('ismaster')
        db_status = "connected"
    except:
        db_status = "disconnected"
    
    return jsonify({
        "status": "healthy",
        "service": "Shipliyo SMS Backend",
        "timestamp": datetime.now().isoformat(),
        "database": db_status,
        "version": "2.0.0",
        "endpoints": {
            "legacy": "/gateway-sms",
            "new": "/incoming-sms", 
            "api": "/api/sms",
            "search": "/api/search-sms"
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))  # 8000 yapın
    print(f"🚀 Server starting on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)