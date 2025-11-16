import re
import html

class InputValidator:
    @staticmethod
    def validate_phone(phone):
        if not phone:
            return False, "Telefon numarası boş olamaz"
        if not re.match(r'^\d+$', phone):
            return False, "Sadece rakam içermeli"
        if len(phone) < 9 or len(phone) > 15:
            return False, "9-15 karakter arasında olmalı"
        return True, None
    
    @staticmethod
    def sanitize_message(message, max_length=500):
        if not message:
            return False, "Mesaj boş olamaz"
        if len(message) > max_length:
            return False, f"Mesaj çok uzun (max {max_length} karakter)"
        
        sanitized = html.escape(message.strip())
        
        malicious_patterns = [
            r'<script.*?>.*?</script>',
            r'javascript:',
            r'on\w+=',
            r'SELECT.*FROM',
            r'UNION.*SELECT'
        ]
        
        for pattern in malicious_patterns:
            if re.search(pattern, sanitized, re.IGNORECASE):
                return False, "Geçersiz mesaj içeriği"
        
        return True, sanitized
    
    @staticmethod
    def validate_session_id(session_id):
        if not session_id or len(session_id) > 100:
            return False
        return bool(re.match(r'^[a-zA-Z0-9_\-\.]+$', session_id))

validator = InputValidator()