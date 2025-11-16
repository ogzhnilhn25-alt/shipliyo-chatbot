import re
import os
from sms_parser import SMSParser
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import psycopg2
from response_manager import ResponseManager

class ChatbotManager:
    def __init__(self):
        self.sms_parser = SMSParser()
        self.response_manager = ResponseManager()
        
        # PostgreSQL Connection - Railway environment variable'dan al
        self.db_connected = False
        
        try:
            self.db_connection = self.get_db_connection()
            if self.db_connection:
                self.db_connection.close()
                self.db_connected = True
                print("✅ PostgreSQL'e bağlandı")
        except Exception as e:
            print(f"❌ PostgreSQL bağlantı hatası: {e}")
            self.db_connected = False

    def get_db_connection(self):
        """PostgreSQL bağlantısı oluştur"""
        try:
            database_url = os.environ.get('DATABASE_URL')
            if not database_url:
                print("❌ DATABASE_URL environment variable bulunamadı")
                return None
            
            # SSL modunu zorla
            if "sslmode" not in database_url:
                if "?" in database_url:
                    database_url += "&sslmode=require"
                else:
                    database_url += "?sslmode=require"
            
            conn = psycopg2.connect(database_url)
            return conn
        except Exception as e:
            print(f"❌ PostgreSQL bağlantı hatası: {e}")
            return None

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
            if self.db_connected:
                time_threshold = datetime.now() - timedelta(hours=2)
                
                conn = self.get_db_connection()
                if conn:
                    cur = conn.cursor()
                    # PostgreSQL LIKE sorgusu
                    cur.execute(
                        "SELECT * FROM sms_messages WHERE body ILIKE %s AND timestamp >= %s ORDER BY timestamp DESC LIMIT 1",
                        (f'%{ref_code}%', time_threshold)
                    )
                    found_sms = cur.fetchone()
                    cur.close()
                    conn.close()
                    
                    if found_sms:
                        # PostgreSQL sonucunu dictionary'ye çevir
                        sms_dict = {
                            'body': found_sms[2],  # body sütunu
                            'timestamp': found_sms[3]  # timestamp sütunu
                        }
                        parsed_sms = self.sms_parser.parse_sms(sms_dict['body'], language)
                        return {
                            "success": True,
                            "response": self.response_manager.get_response('reference_found', language).format(
                                site=parsed_sms['site'].title(),
                                code=parsed_sms['verification_code']
                            ),
                            "response_type": "direct",
                            "data": parsed_sms,
                            "source": "postgresql"
                        }
            
            return {
                "success": False,
                "response": self.response_manager.get_response('no_reference', language),
                "response_type": "direct",
                "source": "postgresql"
            }
                
        except Exception as e:
            print(f"❌ PostgreSQL sorgu hatası: {e}")
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

    def _handle_address_request(self, language: str) -> Dict:
        """Adres isteğini işle"""
        return {
            "success": True,
            "response": self._get_address_response(language),
            "response_type": "address"
        }

    def _get_address_response(self, language: str) -> str:
        """Dillere göre adres response'u"""
        responses = {
            'tr': "Teslimat adresiniz için lütfen telefon numaranızın son 9 hanesini girin (örn: 111222333)",
            'en': "For your delivery address, please enter the last 9 digits of your phone number (eg: 111222333)", 
            'bg': "За вашия адрес за доставка, моля въведете последните 9 цифри от телефонния си номер (напр: 111222333)"
        }
        return responses.get(language, responses['tr'])
    
    def get_recent_sms_by_site(self, site: str, seconds: int = 120, language: str = 'tr') -> Dict:
        """
        Belirli siteden son X saniyedeki SMS'leri getir
        """
        try:
            print(f"🔍 ARAMA: Site='{site}', Saniye={seconds}")

            if not self.db_connected:
                print("❌ PostgreSQL bağlı değil")
                return {
                    "success": False,
                    "response": self.response_manager.get_response('no_recent_sms', language).format(
                        site=site.title(),
                        seconds=seconds
                    ),
                    "response_type": "direct",
                    "source": "postgresql_disconnected"
                }

            time_threshold = datetime.now() - timedelta(seconds=seconds)
            print(f"⏰ Zaman filtresi: {time_threshold}")

            conn = self.get_db_connection()
            if not conn:
                return {
                    "success": False,
                    "response": self.response_manager.get_response('no_recent_sms', language).format(
                        site=site.title(),
                        seconds=seconds
                    ),
                    "response_type": "direct",
                    "source": "postgresql"
                }

            cur = conn.cursor()
            
            if site == 'other':
                # Diğer siteler için (trendyol, hepsiburada, n11 hariç)
                cur.execute(
                    "SELECT * FROM sms_messages WHERE body NOT ILIKE %s AND body NOT ILIKE %s AND body NOT ILIKE %s AND timestamp >= %s ORDER BY timestamp DESC LIMIT 10",
                    ('%trendyol%', '%hepsiburada%', '%n11%', time_threshold)
                )
            else:
                # Belirli site için
                site_patterns = {
                    'trendyol': '%trendyol%',
                    'hepsiburada': '%hepsiburada%', 
                    'n11': '%n11%'
                }
                search_pattern = site_patterns.get(site, f'%{site}%')
                
                cur.execute(
                    "SELECT * FROM sms_messages WHERE body ILIKE %s AND timestamp >= %s ORDER BY timestamp DESC LIMIT 10",
                    (search_pattern, time_threshold)
                )

            recent_sms = cur.fetchall()
            cur.close()
            conn.close()

            print(f"📨 Bulunan SMS sayısı: {len(recent_sms)}")

            if not recent_sms:
                return {
                    "success": False,
                    "response": self.response_manager.get_response('no_recent_sms', language).format(
                        site=site.title(),
                        seconds=seconds
                    ),
                    "response_type": "direct",
                    "source": "postgresql"
                }

            # PostgreSQL sonuçlarını dictionary'ye çevir
            parsed_sms_list = []
            for sms in recent_sms:
                sms_dict = {
                    'body': sms[2],  # body sütunu
                    'timestamp': sms[3]  # timestamp sütunu
                }
                parsed_sms = self.sms_parser.parse_sms(sms_dict['body'], language)
                parsed_sms_list.append(parsed_sms)

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
                    "source": "postgresql"
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
                    "source": "postgresql"
                }

        except Exception as e:
            print(f"❌ PostgreSQL sorgu hatası: {e}")
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


if __name__ == "__main__":
    test_chatbot()