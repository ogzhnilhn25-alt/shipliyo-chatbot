import re
import os
import time
from sms_parser import SMSParser
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import psycopg2
from psycopg2 import OperationalError
from response_manager import ResponseManager

class ChatbotManager:
    def __init__(self):
        self.sms_parser = SMSParser()
        self.response_manager = ResponseManager()

    def get_db_connection(self):
        """
        PostgreSQL bağlantısı oluştur (Akıllı Versiyon)
        Önce Private (İç) ağı dener, bulamazsa Public (Dış) ağı dener.
        """
        
        # 1. ADIM: Doğru URL'i Tespit Etme Stratejisi
        db_url = None
        connection_source = "Unknown"

        # Seçenek A: Direkt Private URL var mı?
        if os.environ.get('DATABASE_PRIVATE_URL'):
            db_url = os.environ.get('DATABASE_PRIVATE_URL')
            connection_source = "DATABASE_PRIVATE_URL (Gizli Ağ)"
        
        # Seçenek B: Railway'in otomatik verdiği PG değişkenleri var mı? (En Sağlıklısı)
        elif os.environ.get('PGHOST') and 'ballast' not in os.environ.get('PGHOST', ''):
            try:
                # PG değişkenlerinden URL oluştur
                pghost = os.environ.get('PGHOST')
                pguser = os.environ.get('PGUSER')
                pgpass = os.environ.get('PGPASSWORD')
                pgport = os.environ.get('PGPORT')
                pgdb = os.environ.get('PGDATABASE')
                
                if pghost and pguser and pgdb:
                    db_url = f"postgres://{pguser}:{pgpass}@{pghost}:{pgport}/{pgdb}"
                    connection_source = "PG Variables (Otomatik İç Ağ)"
            except Exception as e:
                print(f"⚠️ PG Değişkenleri ile URL oluşturulamadı: {e}")

        # Seçenek C: Hiçbiri yoksa, eldeki (muhtemelen Public/Ballast) URL'i kullan
        if not db_url:
            db_url = os.environ.get('DATABASE_URL')
            connection_source = "DATABASE_URL (Mevcut Ayar)"

        if not db_url:
            print("❌ HATA: Hiçbir veritabanı adresi bulunamadı!")
            self._print_debug_vars() # Hangi değişkenler var görelim
            return None
        
        # Eğer hala 'ballast' kullanıyorsak uyarı ver
        if 'ballast' in db_url:
            print(f"⚠️ UYARI: Hala Public Proxy ({connection_source}) kullanılıyor. Bağlantı kopabilir.")
        else:
            print(f"✅ İYİ HABER: Internal Network ({connection_source}) kullanılıyor.")

        # SSL modunu ayarla
        if "sslmode" not in db_url:
            symbol = "&" if "?" in db_url else "?"
            db_url += f"{symbol}sslmode=require"

        # 2. ADIM: Bağlantı Denemesi (Retry Mekanizması)
        max_retries = 3
        for attempt in range(max_retries):
            try:
                conn = psycopg2.connect(
                    db_url,
                    keepalives=1,
                    keepalives_idle=30,
                    keepalives_interval=10,
                    keepalives_count=5,
                    connect_timeout=10
                )
                
                # TIMEZONE SENKRONİZASYONU
                cur = conn.cursor()
                cur.execute("SET TIME ZONE 'Europe/Istanbul'")
                cur.close()
                conn.commit()
                
                return conn
            
            except OperationalError as e:
                print(f"⚠️ Chatbot DB Bağlantı hatası (Deneme {attempt+1}/{max_retries}): {e}")
                print(f"🔗 Denenen Kaynak: {connection_source}")
                time.sleep(1)
            except Exception as e:
                print(f"❌ Kritik PostgreSQL bağlantı hatası: {e}")
                return None
        
        # 3. ADIM: Tüm denemeler başarısızsa Dedektif Modunu çalıştır
        print("❌ Chatbot: Veritabanına bağlanılamadı.")
        self._print_debug_vars()
        return None

    def _print_debug_vars(self):
        """Hata anında ortamdaki veritabanı değişkenlerini (değerlerini gizleyerek) listeler"""
        print("🔍 --- DEDEKTİF MODU: Mevcut Çevre Değişkenleri ---")
        try:
            keys = [k for k in os.environ.keys() if 'PG' in k or 'DB' in k or 'DATABASE' in k or 'RAILWAY' in k]
            if not keys:
                print("⚠️ Hiçbir veritabanı değişkeni (PG*, DATABASE*) bulunamadı!")
            for k in keys:
                val = os.environ[k]
                # Değerin içeriğini gizle ama ipucu ver (örn: ballast var mı?)
                hint = "Private/Internal IP"
                if "ballast" in val: hint = "PUBLIC PROXY (Sorunlu)"
                elif val.startswith("postgres://"): hint = "Connection String"
                print(f"   🔑 {k}: [{hint}]")
            print("------------------------------------------------")
        except:
            pass

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
        
        for intent, keywords_by_lang in intent_keywords.items():
            keywords = keywords_by_lang.get(language, [])
            if any(keyword in message_lower for keyword in keywords):
                return intent
        
        if re.match(r'^[a-zA-Z0-9]{4,6}$', message_lower):
            return 'reference_code'
        
        return 'unknown'

    def handle_message(self, message: str, session_id: str, language: str = 'tr') -> Dict:
        """Gelen mesajı işler ve uygun yanıtı döndürür"""
        message = message.strip().lower()
        
        if message == 'get_code':
            return self._handle_site_selection_bubbles(language)
        elif message == 'help':
            return self._handle_help_request(language)
        elif message in ['trendyol', 'hepsiburada', 'n11', 'other']:
            return self.get_recent_sms_by_site(message, 120, language)
        elif message == 'get_address':
            return self._handle_address_request(language)

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
        return {
            "success": True,
            "response": self.response_manager.get_response('welcome', language),
            "response_type": "bubbles",
            "bubbles": self.response_manager.get_main_menu_bubbles(language)
        }
    
    def _handle_site_selection_bubbles(self, language: str) -> Dict:
        return {
            "success": True,
            "response": self.response_manager.get_response('choose_site', language),
            "response_type": "bubbles", 
            "bubbles": self.response_manager.get_site_bubbles(language)
        }

    def _handle_reference_code(self, ref_code: str, language: str) -> Dict:
        """Referans kodu ile SMS arama"""
        conn = None
        try:
            conn = self.get_db_connection()
            if not conn:
                raise Exception("DB Bağlantısı yok")

            time_threshold = datetime.now() - timedelta(hours=2)
            cur = conn.cursor()
            
            cur.execute(
                "SELECT * FROM sms_messages WHERE body ILIKE %s AND timestamp >= %s ORDER BY timestamp DESC LIMIT 1",
                (f'%{ref_code}%', time_threshold)
            )
            found_sms = cur.fetchone()
            cur.close()
            
            if found_sms:
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
            print(f"❌ PostgreSQL sorgu hatası (_handle_reference_code): {e}")
            return {
                "success": False,
                "response": self.response_manager.get_response('no_reference', language),
                "response_type": "direct",
                "source": "error"
            }
        finally:
            if conn: conn.close()
    
    def _handle_help_request(self, language: str) -> Dict:
        return {
            "success": True,
            "response": self.response_manager.get_help_response(language),
            "response_type": "direct"
        }

    def _handle_address_request(self, language: str) -> Dict:
        return {
            "success": True,
            "response": self._get_address_response(language),
            "response_type": "address"
        }

    def _get_address_response(self, language: str) -> str:
        responses = {
            'tr': "Teslimat adresiniz için lütfen telefon numaranızın son 9 hanesini girin (örn: 111222333)",
            'en': "For your delivery address, please enter the last 9 digits of your phone number (eg: 111222333)", 
            'bg': "За вашия адрес за доставка, моля въведете последните 9 цифри от телефонния си номер (напр: 111222333)"
        }
        return responses.get(language, responses['tr'])
    
    def get_recent_sms_by_site(self, site: str, seconds: int = 120, language: str = 'tr') -> Dict:
        conn = None
        try:
            print(f"🔍 ARAMA: Site='{site}', Saniye={seconds}")
            
            # UTC zamanını kullan
            time_threshold = datetime.utcnow() - timedelta(seconds=seconds)
            
            conn = self.get_db_connection()
            if not conn:
                # Veritabanı yoksa graceful fail
                return {
                    "success": False,
                    "response": self.response_manager.get_response('no_recent_sms', language).format(
                        site=site.title(),
                        seconds=seconds
                    ),
                    "response_type": "direct",
                    "source": "postgresql_error"
                }

            cur = conn.cursor()
            
            if site == 'other':
                cur.execute(
                    "SELECT * FROM sms_messages WHERE body NOT ILIKE %s AND body NOT ILIKE %s AND body NOT ILIKE %s AND timestamp >= %s ORDER BY timestamp DESC LIMIT 10",
                    ('%trendyol%', '%hepsiburada%', '%n11%', time_threshold)
                )
            else:
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
            # conn.close() burada değil, finally bloğunda yapılacak

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

            parsed_sms_list = []
            for sms in recent_sms:
                try:
                    sms_dict = {
                        'body': sms[2],  # body sütunu
                        'timestamp': sms[3]  # timestamp sütunu
                    }
                    parsed_sms = self.sms_parser.parse_sms(sms_dict['body'], language)
                    # Raw body'yi de ekleyelim ki parser hata verirse görelim
                    parsed_sms['raw'] = sms_dict['body']
                    parsed_sms_list.append(parsed_sms)
                except Exception as parse_error:
                    print(f"⚠️ SMS Parse Hatası: {parse_error}")
                    continue

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
                # Çoklu sonuç
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
            print(f"❌ PostgreSQL sorgu hatası (get_recent_sms): {e}")
            return {
                "success": False,
                "response": self.response_manager.get_response('no_recent_sms', language).format(
                    site=site.title(),
                    seconds=seconds
                ),
                "response_type": "direct",
                "source": "error"
            }
        finally:
            if conn: conn.close()