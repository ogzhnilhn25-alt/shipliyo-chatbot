// Dil değişkeni - varsayılan Türkçe
let currentLanguage = 'tr';

// Dil çevirileri
const translations = {
    'tr': {
        'sendButton': 'Gönder',
        'inputPlaceholder': 'Mesajınızı yazın...',
        'userPrefix': 'Sen:',
        'botPrefix': 'Bot:',
        'noMessage': 'Bu referans kodu ile eşleşen mesaj bulunamadı.',
        'error': 'Hata oluştu:'
    },
    'en': {
        'sendButton': 'Send',
        'inputPlaceholder': 'Type your message...',
        'userPrefix': 'You:',
        'botPrefix': 'Bot:',
        'noMessage': 'No message found with this reference code.',
        'error': 'Error:'
    },
    'bg': {
        'sendButton': 'Изпрати',
        'inputPlaceholder': 'Напишете вашето съобщение...',
        'userPrefix': 'Вие:',
        'botPrefix': 'Бот:',
        'noMessage': 'Не е намерено съобщение с този референтен код.',
        'error': 'Грешка:'
    }
};

// Çeviri fonksiyonu
function t(key) {
    return translations[currentLanguage][key] || key;
}

// Dil değiştirme fonksiyonu
function changeLanguage(lang) {
    currentLanguage = lang;
    updateUI();
}

// UI'ı güncelleme fonksiyonu
function updateUI() {
    // Send butonunu güncelle
    if (send) {
        send.textContent = t('sendButton');
    }
    
    // Input placeholder'ı güncelle
    if (input) {
        input.placeholder = t('inputPlaceholder');
    }
}

const chatbox = document.getElementById("chatbox");
const input = document.getElementById("input");
const send = document.getElementById("send");

send.addEventListener("click", async () => {
    const ref = input.value.trim();
    if (!ref) return;

    // Kullanıcı mesajını ekle
    chatbox.innerHTML += `<div class="user">${t('userPrefix')} ${ref}</div>`;

    try {
        const res = await fetch(`/messages?ref=${encodeURIComponent(ref)}`);
        const data = await res.json();

        if (data.found) {
            chatbox.innerHTML += `<div class="bot">${t('botPrefix')} ${data.message}</div>`;
        } else {
            chatbox.innerHTML += `<div class="bot">${t('botPrefix')} ${t('noMessage')}</div>`;
        }
    } catch (err) {
        chatbox.innerHTML += `<div class="bot">${t('botPrefix')} ${t('error')} ${err}</div>`;
    }

    chatbox.scrollTop = chatbox.scrollHeight;
    input.value = "";
});

// Sayfa yüklendiğinde UI'ı güncelle
document.addEventListener('DOMContentLoaded', function() {
    updateUI();
});