import re
import os
from sms_parser import SMSParser
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pymongo import MongoClient
from response_manager import ResponseManager

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
            'get_address': {
                'tr': ['adres', 'adresi', 'teslimat', 'adresim', 'adres al'],
        'bg': ['адрес', 'адресът', 'доставка', 'адреса ми', 'получи адрес'],
        'en': ['address', 'delivery', 'my address', 'get address']
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
        elif message == 'get_address':
    return self._handle_address_request(language)

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
        return bool(re.match(r'^[a-zA-Z0-9]{4,6}$', message))
    
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
            
            return {
                "success": False,
                "response": self.response_manager.get_response('no_reference', language),
                "response_type": "direct",
                "source": "mongodb"
            }
                
        except Exception as e:
            print(f"❌ MongoDB sorgu hatası: {e}")
            return {
                "success": False,
                "response": self.response_manager.get_response('no_reference', language),
                "response_type": "direct",
                "source": "error"
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
            print(f"🔍 ARAMA: Site='{site}', Saniye={seconds}")

            if not self.mongo_connected:
                print("❌ MongoDB bağlı değil")
                return {
                    "success": False,
                    "response": self.response_manager.get_response('no_recent_sms', language).format(
                        site=site.title(),
                        seconds=seconds
                    ),
                    "response_type": "direct",
                    "source": "mongodb_disconnected"
                }

            time_threshold = datetime.now() - timedelta(seconds=seconds)
            print(f"⏰ Zaman filtresi: {time_threshold}")

            site_patterns = {
                'trendyol': r'trendyol|trend',
                'hepsiburada': r'hepsiburada|hepsi',
                'n11': r'n11\.com|n11',
                'other': r''
            }

            search_pattern = site_patterns.get(site, site)
            print(f"🔎 Search pattern: {search_pattern}")

            if site == 'other':
                query = {
                    'body': {'$not': {'$regex': r'trendyol|hepsiburada|n11', '$options': 'i'}},
                    'timestamp': {'$gte': time_threshold}
                }
            else:
                query = {
                    'body': {'$regex': search_pattern, '$options': 'i'},
                    'timestamp': {'$gte': time_threshold}
                }

            print(f"📋 MongoDB Query: {query}")

            recent_sms = list(self.db.sms_messages.find(query).sort('timestamp', -1).limit(10))
            print(f"📨 Bulunan SMS sayısı: {len(recent_sms)}")

            if not recent_sms:
                return {
                    "success": False,
                    "response": self.response_manager.get_response('no_recent_sms', language).format(
                        site=site.title(),
                        seconds=seconds
                    ),
                    "response_type": "direct",
                    "source": "mongodb"
                }

            parsed_sms_list = [self.sms_parser.parse_sms(sms['body'], language) for sms in recent_sms]
            print(f"🔧 Parsed SMS List: {parsed_sms_list}")

            if len(parsed_sms_list) == 1:
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
            else:
                sms_details = [
                    {"site": sms['site'].title(), "code": sms['verification_code'], "raw": sms.get('raw', '')}
                    for sms in parsed_sms_list
                ]
                response_text = self.response_manager.get_response('multiple_sms_found', language).format(
                    count=len(parsed_sms_list),
                    seconds=seconds
                )
                return {
                    "success": True,
                    "response": response_text,
                    "response_type": "list",
                    "sms_list": sms_details,
                    "source": "mongodb"
                }

        except Exception as e:
            print(f"❌ MongoDB sorgu hatası: {e}")
            return {
                "success": False,
                "response": self.response_manager.get_response('no_recent_sms', language).format(
                    site=site.title(),
                    seconds=seconds
                ),
                "response_type": "direct",
                "source": "error"
            }


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
def _handle_address_request(self, language: str) -> Dict:
    """Adres isteğini işle"""
    return {
        "success": True,
        "response": "Teslimat adresiniz için lütfen telefon numaranızın son 9 hanesini girin (örn: 111222333)",
        "response_type": "address"
    }


if __name__ == "__main__":
    test_chatbot()
