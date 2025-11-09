class ResponseManager:
    def __init__(self):
        self.responses = {
            'tr': {
                'welcome': "Hoş geldiniz! Size nasıl yardımcı olabilirim?",
                'reference_found': "✅ {site} onay kodunuz: {code}",
                'no_reference': "❌ Bu referans koduyla mesaj bulunamadı",
                'choose_site': "📱 Hangi siteden kod istiyorsunuz?",
                'get_code_intent': "Lütfen SMS onay kodunu gönderin veya 'kod' yazın",
                'site_options': "Lütfen bir site seçin:",
                'invalid_choice': "❌ Geçersiz seçim. Lütfen listeden bir seçenek belirtin:",
                'processing': "⏳ İsteğiniz işleniyor...",
                'multiple_sms_found': "📨 Son {seconds} saniyede {count} mesaj bulundu:",
                'no_recent_sms': "❌ Son {seconds} saniyede {site} mesajı bulunamadı",
                'unknown_message': "🤔 Anlayamadım. Referans kodu girin veya 'kod' yazın.",
                'help_response': '''
📋 **Kullanım Kılavuzu:**
• SMS onay kodunu doğrudan gönderin (örn: A1B2C3)
• "kod" yazarak site seçimine gidin
• "yardım" yazarak bu bilgiyi görün

📍 **Desteklenen Siteler:** Trendyol, Hepsiburada, N11
                '''
            },
            'bg': {
                'welcome': "Добре дошли! Как мога да ви помогна?",
                'reference_found': "✅ {site} потвърдителен код: {code}",
                'no_reference': "❌ Не е намерено съобщение с този референтен код",
                'choose_site': "📱 От кой сайт искате код?",
                'get_code_intent': "Моля, изпратете SMS с код или напишете 'код'",
                'site_options': "Моля, изберете сайт:",
                'invalid_choice': "❌ Невалиден избор. Моля, изберете от списъка:",
                'processing': "⏳ Обработвам вашата заявка...",
                'multiple_sms_found': "📨 Намерени {count} съобщения през последните {seconds} секунди:",
                'no_recent_sms': "❌ Не са намерени {site} съобщения през последните {seconds} секунди",
                'unknown_message': "🤔 Не разбирам. Въведете референтен код или напишете 'код'.",
                'help_response': '''
📋 **Наръчник за употреба:**
• Изпратете кода за потвърждение директно (напр: A1B2C3)
• Напишете "код", за да изберете сайт
• Напишете "помощ" за тази информация

📍 **Поддържани сайтове:** Trendyol, Hepsiburada, N11
                '''
            },
            'en': {
                'welcome': "Welcome! How can I help you?",
                'reference_found': "✅ {site} verification code: {code}",
                'no_reference': "❌ No message found with this reference code",
                'choose_site': "📱 Which site do you want the code from?",
                'get_code_intent': "Please send the SMS verification code or type 'code'",
                'site_options': "Please select a site:",
                'invalid_choice': "❌ Invalid choice. Please select from the list:",
                'processing': "⏳ Processing your request...",
                'multiple_sms_found': "📨 Found {count} messages in the last {seconds} seconds:",
                'no_recent_sms': "❌ No {site} messages found in the last {seconds} seconds",
                'unknown_message': "🤔 I don't understand. Enter a reference code or type 'code'.",
                'help_response': '''
📋 **Usage Guide:**
• Send the verification code directly (eg: A1B2C3)
• Type "code" to choose a site  
• Type "help" for this information

📍 **Supported Sites:** Trendyol, Hepsiburada, N11
                '''
            }
        }

    def get_response(self, key, language='tr', **kwargs):
        """Dil ve anahtara göre response döndürür"""
        try:
            if language not in self.responses:
                language = 'tr'  # Fallback to Turkish
            
            response_text = self.responses[language].get(key, self.responses['tr'].get(key, key))
            
            # Eğer formatlanacak değişkenler varsa
            if kwargs:
                response_text = response_text.format(**kwargs)
                
            return response_text
            
        except Exception as e:
            print(f"Response error: {e}")
            return f"Error: {key}"

    def get_site_options(self, language='tr'):
        """Site seçeneklerini döndürür"""
        try:
            if language not in self.responses:
                language = 'tr'
                
            options = self.responses[language].get('options', {})
            return [{'label': label, 'value': value} for value, label in options.items()]
            
        except Exception as e:
            print(f"Options error: {e}")
            return []

    def get_available_languages(self):
        """Desteklenen dilleri döndürür"""
        return list(self.responses.keys())

    def get_help_response(self, language='tr'):
        """Yardım mesajını döndürür"""
        return self.get_response('help_response', language)

    def get_welcome_message(self, language='tr'):
        """Hoş geldin mesajını döndürür"""
        return self.get_response('welcome', language)

    def format_reference_found(self, site, code, language='tr'):
        """Referans kodu bulundu mesajını formatlar"""
        return self.get_response('reference_found', language, site=site, code=code)

    def format_multiple_sms_found(self, count, seconds, language='tr'):
        """Çoklu SMS bulundu mesajını formatlar"""
        return self.get_response('multiple_sms_found', language, count=count, seconds=seconds)

    def format_no_recent_sms(self, site, seconds, language='tr'):
        """Son SMS bulunamadı mesajını formatlar"""
        return self.get_response('no_recent_sms', language, site=site, seconds=seconds)

    # YENİ BALONCUK FONKSİYONLARI
    def get_main_menu_bubbles(self, language='tr'):
        """İlk ekran baloncukları"""
        bubbles = {
            'tr': [
                {"title": "📱 Kod Al", "payload": "get_code"},
                {"title": "❓ Yardım", "payload": "help"}
            ],
            'bg': [
                {"title": "📱 Вземи код", "payload": "get_code"},
                {"title": "❓ Помощ", "payload": "help"}
            ],
            'en': [
                {"title": "📱 Get Code", "payload": "get_code"},
                {"title": "❓ Help", "payload": "help"}
            ]
        }
        return bubbles.get(language, bubbles['tr'])

    def get_site_bubbles(self, language='tr'):
        """Site seçim baloncukları"""
        bubbles = {
            'tr': [
                {"title": "🛍️ Trendyol", "payload": "trendyol"},
                {"title": "📦 Hepsiburada", "payload": "hepsiburada"},
                {"title": "🏪 N11", "payload": "n11"},
                {"title": "🔍 Diğer Siteler", "payload": "other"}
            ],
            'bg': [
                {"title": "🛍️ Trendyol", "payload": "trendyol"},
                {"title": "📦 Hepsiburada", "payload": "hepsiburada"},
                {"title": "🏪 N11", "payload": "n11"},
                {"title": "🔍 Други сайтове", "payload": "other"}
            ],
            'en': [
                {"title": "🛍️ Trendyol", "payload": "trendyol"},
                {"title": "📦 Hepsiburada", "payload": "hepsiburada"},
                {"title": "🏪 N11", "payload": "n11"},
                {"title": "🔍 Other Sites", "payload": "other"}
            ]
        }
        return bubbles.get(language, bubbles['tr'])


# Test fonksiyonu - GÜNCELLENMİŞ
def test_response_manager():
    """ResponseManager testleri"""
    rm = ResponseManager()
    
    print("=== ResponseManager Test ===")
    
    # Baloncuk testleri
    print("📋 Ana Menü Baloncukları (TR):", [b['title'] for b in rm.get_main_menu_bubbles('tr')])
    print("📋 Ana Menü Baloncukları (BG):", [b['title'] for b in rm.get_main_menu_bubbles('bg')])
    print("📋 Site Baloncukları (TR):", [b['title'] for b in rm.get_site_bubbles('tr')])
    
    # Dil desteği testi
    print("\n🌍 Desteklenen diller:", rm.get_available_languages())

if __name__ == "__main__":
    test_response_manager()