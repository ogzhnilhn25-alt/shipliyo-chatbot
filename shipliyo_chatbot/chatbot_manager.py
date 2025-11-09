import re
from sms_parser import SMSParser
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pymongo import MongoClient

# ResponseManager'ı ayrı dosyadan import ediyoruz
from response_manager import ResponseManager

import os
# ... diğer import'lar

class ChatbotManager:
    def __init__(self):
        self.sms_parser = SMSParser()
        self.response_manager = ResponseManager()
        
        # MongoDB Connection - Heroku environment variable'dan al
        mongodb_uri = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/')
        
        try:
            self.mongo_client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
            self.db = self.mongo_client.shipliyo_sms
            self.mongo_client.admin.command('ismaster')
            self.mongo_connected = True
            print("✅ MongoDB'ye bağlandı")
        except Exception as e:
            print(f"❌ MongoDB bağlantı hatası: {e}")
            self.mongo_connected = False
        
        # Demo data her zaman hazır
        self.demo_sms_data = self._create_demo_data()        return [
            {
                "body": "Trendyol onay kodunuz: 123456 Ref: A1B2C3",
                "timestamp": datetime.now() - timedelta(seconds=30),
                "site": "trendyol",
                "ref_code": "A1B2C3",
                "verification_code": "123456"
            },
            {
                "body": "Hepsiburada güvenlik kodu: 654321 No: XYZ789", 
                "timestamp": datetime.now() - timedelta(seconds=45),
                "site": "hepsiburada",
                "ref_code": "XYZ789",
                "verification_code": "654321"
            },
            {
                "body": "n11.com doğrulama kodu: 111222 Referans: TEST12",
                "timestamp": datetime.now() - timedelta(seconds=60),
                "site": "n11", 
                "ref_code": "TEST12",
                "verification_code": "111222"
            }
        ]
    
    def detect_intent(self, message: str, language: str) -> str:
        """Mesajın intent'ini tespit eder"""
        message_lower = message.lower().strip()
        
        # Intent keyword mapping
        intent_keywords = {
            'get_code': {
                'tr': ['kod', 'kodu', 'onay', 'doğrulama', 'numara', 'almak', 'istiyorum'],
                'bg': ['код', 'кодът', 'кодове', 'потвърдителен', 'искам', 'получи'],
                'en': ['code', 'verification', 'number', 'want', 'get']
            },
            'help': {
                'tr': ['yardım', 'yardim', 'help', 'nasıl', 'ne yapabilir'],
                'bg': ['помощ', 'помогнете', 'help', 'как', 'какво'],
                'en': ['help', 'yardım', 'how', 'what can you do']
            }
        }
        
        # Check each intent for current language
        for intent, keywords_by_lang in intent_keywords.items():
            keywords = keywords_by_lang.get(language, [])
            if any(keyword in message_lower for keyword in keywords):
                return intent
        
        # Referans kodu pattern'i
        if re.match(r'^[a-zA-Z0-9]{4,6}$', message_lower):
            return 'reference_code'
        
        return 'unknown'

    def handle_message(self, message: str, session_id: str, language: str = 'tr') -> Dict:
        """Gelen mesajı işler ve uygun yanıtı döndürür"""
        message = message.strip().lower()
        
        # Baloncuk payload'larını kontrol et
        if message == 'get_code':
            return self._handle_site_selection_bubbles(language)
        elif message == 'help':
            return self._handle_help_request(language)
        elif message in ['trendyol', 'hepsiburada', 'n11', 'other']:
            return self.get_recent_sms_by_site(message, 120, language)
        
        # Eski sistemle uyumluluk
        intent = self.detect_intent(message, language)
        if intent == 'reference_code':
            return self._handle_reference_code(message, language)
        elif intent == 'get_code':
            return self._handle_site_selection_bubbles(language)
        elif intent == 'help':
            return self._handle_help_request(language)
        else:
            return self._handle_main_menu(language)
    
    def _handle_main_menu(self, language: str) -> Dict:
        """Ana menü baloncukları"""
        return {
            "success": True,
            "response": self.response_manager.get_response('welcome', language),
            "response_type": "bubbles",
            "bubbles": self.response_manager.get_main_menu_bubbles(language)
        }
    
    def _handle_site_selection_bubbles(self, language: str) -> Dict:
        """Site seçim baloncukları"""
        return {
            "success": True,
            "response": self.response_manager.get_response('choose_site', language),
            "response_type": "bubbles", 
            "bubbles": self.response_manager.get_site_bubbles(language)
        }

    def _looks_like_reference_code(self, message: str) -> bool:
        """Mesaj referans kodu gibi görünüyor mu?"""
        # 4-6 haneli alfanumerik
        if re.match(r'^[a-zA-Z0-9]{4,6}$', message):
            return True
        return False
    
    def _handle_reference_code(self, ref_code: str, language: str) -> Dict:
        """Referans kodu ile SMS arama"""
        try:
            if self.mongo_connected:
                time_threshold = datetime.now() - timedelta(hours=2)
                found_sms = self.db.sms_messages.find_one({
                    'body': {'$regex': ref_code, '$options': 'i'},
                    'timestamp': {'$gte': time_threshold}
                })
                
                if found_sms:
                    parsed_sms = self.sms_parser.parse_sms(found_sms['body'], language)
                    return {
                        "success": True,
                        "response": self.response_manager.get_response('reference_found', language).format(
                            site=parsed_sms['site'].title(),
                            code=parsed_sms['verification_code']
                        ),
                        "response_type": "direct",
                        "data": parsed_sms,
                        "source": "mongodb"
                    }
            
            return self._handle_reference_code_demo(ref_code, language)
                
        except Exception as e:
            print(f"❌ MongoDB sorgu hatası: {e}")
            return self._handle_reference_code_demo(ref_code, language)
    
    def _handle_reference_code_demo(self, ref_code: str, language: str) -> Dict:
        """Demo fallback"""
        found_sms = None
        demo_data = self._create_demo_data()
        
        for sms in demo_data:
            if sms['ref_code'] and sms['ref_code'].lower() == ref_code.lower():
                found_sms = sms
                break
        
        if found_sms:
            return {
                "success": True,
                "response": self.response_manager.get_response('reference_found', language).format(
                    site=found_sms['site'].title(),
                    code=found_sms['verification_code']
                ),
                "response_type": "direct",
                "data": found_sms,
                "source": "demo"
            }
        else:
            return {
                "success": False,
                "response": self.response_manager.get_response('no_reference', language),
                "response_type": "direct",
                "source": "demo"
            }
    
    def _handle_help_request(self, language: str) -> Dict:
        """Yardım mesajı gönder"""
        return {
            "success": True,
            "response": self.response_manager.get_help_response(language),
            "response_type": "direct"
        }
    
    def _handle_unknown_message(self, message: str, language: str) -> Dict:
        """Bilinmeyen mesaj için yanıt"""
        return {
            "success": False,
            "response": self.response_manager.get_response('unknown_message', language),
            "response_type": "direct"
        }
    
    def get_recent_sms_by_site(self, site: str, seconds: int = 120, language: str = 'tr') -> Dict:
        """
        Belirli siteden son X saniyedeki SMS'leri getir
        """
        try:
            if self.mongo_connected:
                # MongoDB'den gerçek veri
                time_threshold = datetime.now() - timedelta(seconds=seconds)
                
                recent_sms = list(self.db.sms_messages.find({
                    'body': {'$regex': site, '$options': 'i'},
                    'timestamp': {'$gte': time_threshold}
                }).sort('timestamp', -1).limit(10))
                
                if recent_sms:
                    # SMS'leri parse et
                    parsed_sms_list = []
                    for sms in recent_sms:
                        parsed = self.sms_parser.parse_sms(sms['body'], language)
                        parsed_sms_list.append(parsed)
                    
                    if len(parsed_sms_list) > 1:
                        return {
                            "success": True,
                            "response": self.response_manager.get_response('multiple_sms_found', language).format(
                                count=len(parsed_sms_list),
                                seconds=seconds
                            ),
                            "response_type": "list",
                            "sms_list": parsed_sms_list,
                            "source": "mongodb"
                        }
                    else:
                        sms = parsed_sms_list[0]
                        return {
                            "success": True,
                            "response": self.response_manager.get_response('reference_found', language).format(
                                site=sms['site'].title(),
                                code=sms['verification_code']
                            ),
                            "response_type": "direct",
                            "data": sms,
                            "source": "mongodb"
                        }
            
            # Fallback to demo
            return self._get_recent_sms_demo(site, seconds, language)
            
        except Exception as e:
            print(f"❌ MongoDB sorgu hatası: {e}")
            return self._get_recent_sms_demo(site, seconds, language)
    
    def _get_recent_sms_demo(self, site: str, seconds: int = 120, language: str = 'tr') -> Dict:
        """Demo fallback for recent SMS"""
        now = datetime.now()
        recent_sms = [
            sms for sms in self.demo_sms_data
            if sms['site'] == site and (now - sms['timestamp']).total_seconds() <= seconds
        ]
        
        if recent_sms:
            if len(recent_sms) > 1:
                return {
                    "success": True,
                    "response": self.response_manager.get_response('multiple_sms_found', language).format(
                        count=len(recent_sms),
                        seconds=seconds
                    ),
                    "response_type": "list",
                    "sms_list": recent_sms,
                    "source": "demo"
                }
            else:
                sms = recent_sms[0]
                return {
                    "success": True,
                    "response": self.response_manager.get_response('reference_found', language).format(
                        site=sms['site'].title(),
                        code=sms['verification_code']
                    ),
                    "response_type": "direct",
                    "data": sms,
                    "source": "demo"
                }
        else:
            return {
                "success": False,
                "response": self.response_manager.get_response('no_recent_sms', language).format(
                    site=site.title(),
                    seconds=seconds
                ),
                "response_type": "direct",
                "source": "demo"
            }


# Test - GÜNCELLENMİŞ
def test_chatbot():
    """Chatbot testleri"""
    chatbot = ChatbotManager()
    
    test_cases = [
        "",  # Boş mesaj -> Ana menü
        "get_code",  # Kod Al -> Site seçim
        "trendyol",  # Trendyol -> SMS listele
        "help",  # Yardım
        "A1B2C3",  # Referans kodu
        "merhaba"  # Bilinmeyen -> Ana menü
    ]
    
    for message in test_cases:
        print(f"💬 Müşteri: '{message}'")
        response = chatbot.handle_message(message, "test_session", "tr")
        print(f"✅ Success: {response['success']}")
        print(f"📝 Response: {response['response']}")
        if 'bubbles' in response:
            print(f"🫧 Bubbles: {[b['title'] for b in response['bubbles']]}")
        print("─" * 50)

if __name__ == "__main__":
    test_chatbot()