import re
from typing import Dict, Optional

class SMSParser:
    """
    Çok dilli SMS parser - Türkçe, Bulgarca, İngilizce
    """
    
    # Çok dilli site tespiti
    SITE_KEYWORDS = {
        'trendyol': {
            'tr': ['trendyol', 'trend'],
            'bg': ['trendyol'],
            'en': ['trendyol']
        },
        'hepsiburada': {
            'tr': ['hepsiburada', 'hepsi', 'hb'],
            'bg': ['hepsiburada'],
            'en': ['hepsiburada']
        },
        'n11': {
            'tr': ['n11', 'n11.com'],
            'bg': ['n11'],
            'en': ['n11']
        },
        'amazon': {
            'tr': ['amazon'],
            'bg': ['amazon'],
            'en': ['amazon', 'amzn']
        }
    }
    
    # Çok dilli referans kodu pattern'leri
    REF_PATTERNS = {
        'tr': [
            r'ref[:\s]*([a-zA-Z0-9]{4,6})',
            r'referans[:\s]*([a-zA-Z0-9]{4,6})',
            r'no[:\s]*([a-zA-Z0-9]{4,6})',
            r'kod[:\s]*([a-zA-Z0-9]{4,6})',
            r'kodu[:\s]*([a-zA-Z0-9]{4,6})',
            r'numara[:\s]*([a-zA-Z0-9]{4,6})'
        ],
        'bg': [
            r'ref[:\s]*([a-zA-Z0-9]{4,6})',
            r'referans[:\s]*([a-zA-Z0-9]{4,6})',
            r'nomer[:\s]*([a-zA-Z0-9]{4,6})',
            r'kod[:\s]*([a-zA-Z0-9]{4,6})'
        ],
        'en': [
            r'ref[:\s]*([a-zA-Z0-9]{4,6})',
            r'reference[:\s]*([a-zA-Z0-9]{4,6})',
            r'code[:\s]*([a-zA-Z0-9]{4,6})',
            r'number[:\s]*([a-zA-Z0-9]{4,6})',
            r'ref[.\s]*([a-zA-Z0-9]{4,6})'
        ]
    }
    
    # Çok dilli doğrulama kodu pattern'leri - 5 ve 6 haneli
    VERIFICATION_PATTERNS = {
        'tr': [
            r'(\d{5,6})',                    # 5-6 haneli sayılar
            r'kodu[:\s]*(\d{5,6})',          # 5-6 haneli
            r'kod[:\s]*(\d{5,6})',           # 5-6 haneli
            r'onay[:\s]*kodu[:\s]*(\d{5,6})' # 5-6 haneli
        ],
        'bg': [
            r'(\d{5,6})',
            r'kod[:\s]*(\d{5,6})',
            r'potvърditelen[:\s]*kod[:\s]*(\d{5,6})'
        ],
        'en': [
            r'(\d{5,6})',
            r'code[:\s]*(\d{5,6})',
            r'verification[:\s]*code[:\s]*(\d{5,6})',
            r'confirm[:\s]*code[:\s]*(\d{5,6})'
        ]
    }
    
    def parse_sms(self, sms_body: str, language: str = 'tr') -> Dict:
        """
        SMS'i belirtilen dilde parse eder
        """
        sms_lower = sms_body.lower()
        
        return {
            'original_body': sms_body,  # Orijinal SMS içeriği
            'raw': sms_body,            # RAW alanı - orijinal içerik
            'language': language,
            'site': self._detect_site(sms_lower, language),
            'ref_code': self._extract_ref_code(sms_lower, language),
            'verification_code': self._extract_verification_code(sms_lower, language),
            'code': self._extract_verification_code(sms_lower, language),  # 'code' alanı da ekle
            'has_reference': bool(self._extract_ref_code(sms_lower, language))
        }
    
    def _detect_site(self, sms_body: str, language: str) -> str:
        """
        SMS içeriğinden site adını tespit eder (çok dilli)
        """
        for site, keywords in self.SITE_KEYWORDS.items():
            lang_keywords = keywords.get(language, keywords.get('en', []))
            for keyword in lang_keywords:
                if keyword in sms_body:
                    return site
        return 'other'
    
    def _extract_ref_code(self, sms_body: str, language: str) -> Optional[str]:
        """
        Referans kodunu çıkarır (çok dilli)
        """
        patterns = self.REF_PATTERNS.get(language, self.REF_PATTERNS['en'])
        for pattern in patterns:
            match = re.search(pattern, sms_body)
            if match:
                return match.group(1).upper()
        return None
    
    def _extract_verification_code(self, sms_body: str, language: str) -> Optional[str]:
        """
        Doğrulama kodunu çıkarır (çok dilli)
        """
        patterns = self.VERIFICATION_PATTERNS.get(language, self.VERIFICATION_PATTERNS['en'])
        for pattern in patterns:
            match = re.search(pattern, sms_body)
            if match:
                return match.group(1)
        return None

    def detect_language(self, sms_body: str) -> str:
        """
        SMS'in dilini otomatik tespit eder
        """
        sms_lower = sms_body.lower()
        
        # Bulgarca kelimeler
        bg_keywords = ['потвърдителен', 'код', 'номер', 'рефер']
        # Türkçe kelimeler  
        tr_keywords = ['onay', 'kod', 'numara', 'referans']
        # İngilizce kelimeler
        en_keywords = ['verification', 'code', 'number', 'reference']
        
        bg_count = sum(1 for word in bg_keywords if word in sms_lower)
        tr_count = sum(1 for word in tr_keywords if word in sms_lower) 
        en_count = sum(1 for word in en_keywords if word in sms_lower)
        
        if bg_count > tr_count and bg_count > en_count:
            return 'bg'
        elif tr_count > bg_count and tr_count > en_count:
            return 'tr'
        elif en_count > bg_count and en_count > tr_count:
            return 'en'
        else:
            return 'tr'  # Varsayılan

# Test fonksiyonu - çok dilli
def test_multilingual_parser():
    """Çok dilli parser testleri"""
    parser = SMSParser()
    
    test_sms = [
        # Türkçe
        "Trendyol onay kodunuz: 123456 Ref: A1B2C3",
        # Bulgarca  
        "Trendyol потвърдителен код: 654321 рефер: XYZ789",
        # İngilizce
        "Trendyol verification code: 111222 reference: TEST12",
        # Karışık
        "Hepsiburada kod: 999888 No: AMZ123"
    ]
    
    for sms in test_sms:
        # Dil tespiti
        detected_lang = parser.detect_language(sms)
        result = parser.parse_sms(sms, detected_lang)
        
        print(f"📱 SMS: {sms}")
        print(f"🌍 Dil: {detected_lang}")
        print(f"🔍 Sonuç: {result}")
        print("─" * 50)

if __name__ == "__main__":
    test_multilingual_parser()