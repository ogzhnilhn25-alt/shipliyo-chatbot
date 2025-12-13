// Shipliyo Chat Widget - Backend Entegreli
class ShipliyoWidget {
    constructor() {
        this.isOpen = false;
        this.isLoading = false;
        this.currentView = 'main';
        this.viewHistory = []; // Navigation history
        this.API_BASE_URL = 'https://shipliyo-chatbot-production.up.railway.app';
        
        // ✅ DİL DEĞİŞKENİ EKLENDİ
        this.currentLanguage = 'tr';
        this.translations = {
            'tr': {
                'welcome': 'Merhaba!',
                'helpText': 'Size nasıl yardımcı olabilirim?',
                'online': 'Çevrimiçi',
                'getCode': 'Doğrulama Kodu Al',
                'help': 'Yardım & Bilgi',
                'searchRef': 'Referans Kodu ile Ara',
                'getAddress': 'Teslimat Adresi Al',
                'selectSite': 'Site Seçin',
                'siteDesc': 'Doğrulama kodu almak için bir site seçin',
                'searchRefTitle': 'Referans Kodu Ara',
                'searchRefDesc': 'Referans kodunu girerek arama yapın',
                'refPlaceholder': 'Referans kodunu girin...',
                'addressTitle': 'Teslimat Adresi',
                'addressDesc': 'Telefon numaranızın son 9 hanesini girin',
                'phonePlaceholder': 'Örnek: 111222333',
                'processing': 'İşleniyor...',
                'send': 'Gönder',
                'messagePlaceholder': 'Mesajınızı yazın...',
                'searching': 'aranıyor...',
                'noSms': 'SMS bulunamadı.',
                'error': 'Hata oluştu:',
                'smsFound': 'SMS bulundu:',
                'addressResult': 'TESLİMAT ADRESİNİZ:',
                'turkish': '🇹🇷 Türkçe:',
                'english': '🇬🇧 English:',
                'bulgarian': '🇧🇬 Български:',
                'city': 'İl:',
                'district': 'İlçe:',
                'neighborhood': 'Mahalle:',
                'street': 'Sokak:',
                'buildingNo': 'Kapı No:',
                'invalidPhone': 'Lütfen sadece 9 haneli telefon numarası girin (örn: 111222333)'
            },
            'en': {
                'welcome': 'Hello!',
                'helpText': 'How can I help you?',
                'online': 'Online',
                'getCode': 'Get Verification Code',
                'help': 'Help & Information',
                'searchRef': 'Search by Reference Code',
                'getAddress': 'Get Delivery Address',
                'selectSite': 'Select Site',
                'siteDesc': 'Select a site to get verification code',
                'searchRefTitle': 'Search Reference Code',
                'searchRefDesc': 'Search by entering reference code',
                'refPlaceholder': 'Enter reference code...',
                'addressTitle': 'Delivery Address',
                'addressDesc': 'Enter last 9 digits of your phone number',
                'phonePlaceholder': 'Example: 111222333',
                'processing': 'Processing...',
                'send': 'Send',
                'messagePlaceholder': 'Type your message...',
                'searching': 'searching...',
                'noSms': 'No SMS found.',
                'error': 'Error:',
                'smsFound': 'SMS found:',
                'addressResult': 'YOUR DELIVERY ADDRESS:',
                'turkish': '🇹🇷 Turkish:',
                'english': '🇬🇧 English:',
                'bulgarian': '🇧🇬 Bulgarian:',
                'city': 'City:',
                'district': 'District:',
                'neighborhood': 'Neighborhood:',
                'street': 'Street:',
                'buildingNo': 'Building No:',
                'invalidPhone': 'Please enter only 9-digit phone number (e.g., 111222333)'
            },
            'bg': {
                'welcome': 'Здравейте!',
                'helpText': 'Как мога да ви помогна?',
                'online': 'Онлайн',
                'getCode': 'Вземи код за потвърждение',
                'help': 'Помощ & Информация',
                'searchRef': 'Търсене с референтен код',
                'getAddress': 'Вземи адрес за доставка',
                'selectSite': 'Изберете сайт',
                'siteDesc': 'Изберете сайт, за да получите код за потвърждение',
                'searchRefTitle': 'Търсене на референтен код',
                'searchRefDesc': 'Търсене чрез въвеждане на референтен код',
                'refPlaceholder': 'Въведете референтен код...',
                'addressTitle': 'Адрес за доставка',
                'addressDesc': 'Въведете последните 9 цифри от телефона си',
                'phonePlaceholder': 'Пример: 111222333',
                'processing': 'Обработва се...',
                'send': 'Изпрати',
                'messagePlaceholder': 'Напишете вашето съобщение...',
                'searching': 'търси се...',
                'noSms': 'Не са намерени SMS.',
                'error': 'Грешка:',
                'smsFound': 'Намерени SMS:',
                'addressResult': 'ВАШИЯТ АДРЕС ЗА ДОСТАВКА:',
                'turkish': '🇹🇷 Турски:',
                'english': '🇬🇧 Английски:',
                'bulgarian': '🇧🇬 Български:',
                'city': 'Област:',
                'district': 'Община:',
                'neighborhood': 'Квартал:',
                'street': 'Улица:',
                'buildingNo': 'Номер на сграда:',
                'invalidPhone': 'Моля, въведете само 9-цифрен телефонен номер (напр. 111222333)'
            }
        };
        
        this.init();
    }
    
    // ✅ DİL DEĞİŞTİRME FONKSİYONU EKLENDİ
    setLanguage(lang) {
        if (this.translations[lang]) {
            this.currentLanguage = lang;
            this.updateUITexts();
            console.log('Dil değiştirildi:', lang);
        }
    }
    
    // ✅ ÇEVİRİ FONKSİYONU
    t(key) {
        return this.translations[this.currentLanguage][key] || key;
    }
    
    // ✅ UI METİNLERİNİ GÜNCELLE
    updateUITexts() {
        const t = this.translations[this.currentLanguage];
        
        // Header metinleri
        const headerTitle = document.querySelector('.header-text h3');
        if (headerTitle) headerTitle.textContent = 'Shipliyo Assistant';
        
        const statusText = document.querySelector('.status small');
        if (statusText) statusText.textContent = t.online;
        
        // Welcome section
        const welcomeStrong = document.querySelector('.welcome-text strong');
        if (welcomeStrong) welcomeStrong.textContent = t.welcome;
        
        const welcomeP = document.querySelector('.welcome-text p');
        if (welcomeP) welcomeP.textContent = t.helpText;
        
        // Quick actions
        const actionCards = document.querySelectorAll('.action-card span');
        if (actionCards.length >= 4) {
            actionCards[0].textContent = t.getCode;
            actionCards[1].textContent = t.help;
            actionCards[2].textContent = t.searchRef;
            actionCards[3].textContent = t.getAddress;
        }
        
        // View headers
        const sitesHeader = document.querySelector('#sitesView .view-header h3');
        if (sitesHeader) sitesHeader.textContent = t.selectSite;
        
        const sitesDesc = document.querySelector('#sitesView .view-header p');
        if (sitesDesc) sitesDesc.textContent = t.siteDesc;
        
        const refHeader = document.querySelector('#referenceView .view-header h3');
        if (refHeader) refHeader.textContent = t.searchRefTitle;
        
        const refDesc = document.querySelector('#referenceView .view-header p');
        if (refDesc) refDesc.textContent = t.searchRefDesc;
        
        const addressHeader = document.querySelector('#addressView .view-header h3');
        if (addressHeader) addressHeader.textContent = t.addressTitle;
        
        const addressDesc = document.querySelector('#addressView .view-header p');
        if (addressDesc) addressDesc.textContent = t.addressDesc;
        
        // Input placeholders
        const refInput = document.getElementById('refCodeInput');
        if (refInput) refInput.placeholder = t.refPlaceholder;
        
        const phoneInput = document.getElementById('phoneInput');
        if (phoneInput) phoneInput.placeholder = t.phonePlaceholder;
        
        const chatInput = document.getElementById('chatInput');
        if (chatInput) chatInput.placeholder = t.messagePlaceholder;
        
        // Loading text
        const loadingText = document.querySelector('#loadingState p');
        if (loadingText) loadingText.textContent = t.processing;
    }
    
    init() {
        this.createWidget();
        this.attachEvents();
	this.checkAutoOpen();
    }
    
    createWidget() {
        const widgetHTML = `
            <div id="shipliyoWidget">
                <div id="shipliyoBubble">
                    <div class="bubble-pulse"></div>
                    <span>💬</span>
                </div>
                
                <div id="shipliyoWindow">
                    <div class="widget-header">
                        <div class="header-content">
                            <button class="back-btn" id="backBtn" style="display: none;">
                                <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                                    <path d="M11.354 1.646a.5.5 0 0 1 0 .708L5.707 8l5.647 5.646a.5.5 0 0 1-.708.708l-6-6a.5.5 0 0 1 0-.708l6-6a.5.5 0 0 1 .708 0z"/>
                                </svg>
                            </button>
                            <div class="avatar">🤖</div>
                            <div class="header-text">
                                <h3>Shipliyo Asistan</h3>
                                <div class="status">
                                    <span class="status-dot"></span>
                                    <small>Çevrimiçi</small>
                                </div>
                            </div>
                        </div>
                        
                        <!-- ✅ DİL BUTONLARI HEADER'A EKLENDİ -->
                        <div class="language-buttons">
                            <button class="lang-btn active" data-lang="tr">🇹🇷</button>
                            <button class="lang-btn" data-lang="en">🇺🇸</button>
                            <button class="lang-btn" data-lang="bg">🇧🇬</button>
                        </div>
                        
                        <button class="close-btn">
                            <svg width="14" height="14" viewBox="0 0 14 14" fill="currentColor">
                                <path d="M14 1.41L12.59 0L7 5.59L1.41 0L0 1.41L5.59 7L0 12.59L1.41 14L7 8.41L12.59 14L14 12.59L8.41 7L14 1.41Z"/>
                            </svg>
                        </button>
                    </div>
                    
                    <div class="widget-body">
                        <!-- Main View -->
                        <div class="view-main" id="mainView">
                            <div class="welcome-section">
                                <div class="welcome-avatar">👋</div>
                                <div class="welcome-text">
                                    <strong>Merhaba!</strong>
                                    <p>Size nasıl yardımcı olabilirim?</p>
                                </div>
                            </div>
                            
                            <div class="quick-actions">
                                <div class="action-card" data-action="get_code">
                                    <div class="action-icon">📱</div>
                                    <span>Doğrulama Kodu Al</span>
                                </div>
                                
                                <div class="action-card" data-action="help">
                                    <div class="action-icon">❓</div>
                                    <span>Yardım & Bilgi</span>
                                </div>
                                
                                <div class="action-card" data-action="reference_input">
                                    <div class="action-icon">🔍</div>
                                    <span>Referans Kodu ile Ara</span>
                                </div>
                                
                                <div class="action-card" data-action="get_address">
                                    <div class="action-icon">🏠</div>
                                    <span>Teslimat Adresi Al</span>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Site Selection View -->
                        <div class="view-sites" id="sitesView" style="display: none;">
                            <div class="view-header">
                                <h3>Site Seçin</h3>
                                <p>Doğrulama kodu almak için bir site seçin</p>
                            </div>
                            <div class="sites-grid" id="sitesGrid">
                                <!-- Sites will be loaded here -->
                            </div>
                        </div>
                        
                        <!-- Reference Input View -->
                        <div class="view-reference" id="referenceView" style="display: none;">
                            <div class="view-header">
                                <h3>Referans Kodu Ara</h3>
                                <p>Referans kodunu girerek arama yapın</p>
                            </div>
                            <div class="reference-section">
                                <div class="input-group">
                                    <input type="text" id="refCodeInput" placeholder="Referans kodunu girin...">
                                    <button id="searchRefBtn">
                                        <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                                            <path d="M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001c.03.04.062.078.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1.007 1.007 0 0 0-.115-.1zM12 6.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0z"/>
                                        </svg>
                                    </button>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Address View -->
                        <div class="view-address" id="addressView" style="display: none;">
                            <div class="view-header">
                                <h3>Teslimat Adresi</h3>
                                <p>Telefon numaranızın son 9 hanesini girin</p>
                            </div>
                            
                            <div class="address-section">
                                <div class="input-group">
                                    <input type="text" id="phoneInput" placeholder="Örnek: 111222333" maxlength="9">
                                    <button id="getAddressBtn">
                                        <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                                            <path d="M15.964.686a.5.5 0 0 0-.65-.65L.767 5.855a.5.5 0 0 0-.082.897l3.995 1.94L8 8l.209.004 4.001 1.94a.5.5 0 0 0 .898-.082L15.964.686zm-1.833 1.89L6.637 10.07l-.215-.338a.5.5 0 0 0-.154-.154l-.338-.215 7.494-7.494 1.178-.471-.47 1.178z"/>
                                        </svg>
                                    </button>
                                </div>
                                
                                <div class="address-result" id="addressResult" style="display: none;">
                                    <!-- Adres sonucu burada gösterilecek -->
                                </div>
                            </div>
                        </div>
                        
                        <!-- Chat View -->
                        <div class="view-chat" id="chatView" style="display: none;">
                            <div class="messages-container" id="messagesContainer"></div>
                            <div class="chat-input-container">
                                <div class="input-group">
                                    <input type="text" id="chatInput" placeholder="Mesajınızı yazın...">
                                    <button id="sendMessageBtn">
                                        <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                                            <path d="M15.964.686a.5.5 0 0 0-.65-.65L.767 5.855a.5.5 0 0 0-.082.897l3.995 1.94L8 8l.209.004 4.001 1.94a.5.5 0 0 0 .898-.082L15.964.686zm-1.833 1.89L6.637 10.07l-.215-.338a.5.5 0 0 0-.154-.154l-.338-.215 7.494-7.494 1.178-.471-.47 1.178z"/>
                                        </svg>
                                    </button>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Loading State -->
                        <div class="loading-state" id="loadingState" style="display: none;">
                            <div class="loading-spinner"></div>
                            <p>İşleniyor...</p>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', widgetHTML);
        this.injectStyles();
        this.loadSites();
        this.updateUITexts();
    }
    
    injectStyles() {
        const styles = `
            <style>
                #shipliyoWidget {
                    position: fixed;
                    bottom: 24px;
                    right: 24px;
                    z-index: 10000;
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                }
                
                #shipliyoBubble {
                    width: 64px;
                    height: 64px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    cursor: pointer;
                    box-shadow: 0 8px 32px rgba(102, 126, 234, 0.4);
                    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
                    position: relative;
                    color: white;
                    font-size: 24px;
                }
                
                #shipliyoBubble:hover {
                    transform: scale(1.15) rotate(5deg);
                    box-shadow: 0 12px 40px rgba(102, 126, 234, 0.6);
                }
                
                .bubble-pulse {
                    position: absolute;
                    top: -4px;
                    right: -4px;
                    width: 72px;
                    height: 72px;
                    border: 2px solid rgba(102, 126, 234, 0.4);
                    border-radius: 50%;
                    animation: pulse 2s infinite;
                }
                
                @keyframes pulse {
                    0% { transform: scale(0.8); opacity: 1; }
                    70% { transform: scale(1.2); opacity: 0; }
                    100% { transform: scale(0.8); opacity: 0; }
                }
                
                #shipliyoWindow {
                    position: absolute;
                    bottom: 80px;
                    right: 0;
                    width: 380px;
                    height: 560px;
                    background: white;
                    border-radius: 20px;
                    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
                    display: none;
                    flex-direction: column;
                    overflow: hidden;
                    border: 1px solid rgba(0, 0, 0, 0.05);
                }
                
                .widget-header {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 16px 20px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    min-height: 60px;
                }
                
                .header-content {
                    display: flex;
                    align-items: center;
                    gap: 12px;
                    flex: 1;
                }
                
                /* ✅ DİL BUTONLARI STİLİ */
                .language-buttons {
                    display: flex;
                    gap: 4px;
                    margin-right: 8px;
                }
                
                .lang-btn {
                    width: 32px;
                    height: 32px;
                    border: 1px solid rgba(255, 255, 255, 0.3);
                    background: rgba(255, 255, 255, 0.1);
                    color: white;
                    border-radius: 6px;
                    cursor: pointer;
                    font-size: 12px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    transition: all 0.2s ease;
                }
                
                .lang-btn:hover {
                    background: rgba(255, 255, 255, 0.2);
                    transform: scale(1.1);
                }
                
                .lang-btn.active {
                    background: rgba(255, 255, 255, 0.3);
                    border-color: rgba(255, 255, 255, 0.5);
                    transform: scale(1.1);
                }
                
                .back-btn {
                    background: rgba(255, 255, 255, 0.2);
                    border: none;
                    color: white;
                    width: 32px;
                    height: 32px;
                    border-radius: 8px;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    transition: all 0.2s ease;
                }
                
                .back-btn:hover {
                    background: rgba(255, 255, 255, 0.3);
                }
                
                .avatar {
                    width: 36px;
                    height: 36px;
                    background: rgba(255, 255, 255, 0.2);
                    border-radius: 10px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 16px;
                }
                
                .header-text {
                    flex: 1;
                }
                
                .header-text h3 {
                    margin: 0 0 2px 0;
                    font-size: 16px;
                    font-weight: 600;
                }
                
                .status {
                    display: flex;
                    align-items: center;
                    gap: 6px;
                }
                
                .status-dot {
                    width: 6px;
                    height: 6px;
                    background: #4ade80;
                    border-radius: 50%;
                    animation: blink 2s infinite;
                }
                
                @keyframes blink {
                    0%, 50% { opacity: 1; }
                    51%, 100% { opacity: 0.3; }
                }
                
                .status small {
                    font-size: 11px;
                    opacity: 0.9;
                }
                
                .close-btn {
                    background: rgba(255, 255, 255, 0.2);
                    border: none;
                    color: white;
                    width: 32px;
                    height: 32px;
                    border-radius: 8px;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    transition: all 0.2s ease;
                }
                
                .close-btn:hover {
                    background: rgba(255, 255, 255, 0.3);
                }
                
                .widget-body {
                    flex: 1;
                    padding: 20px;
                    overflow-y: auto;
                    background: #fafbfc;
                }
                
                .welcome-section {
                    display: flex;
                    align-items: flex-start;
                    gap: 12px;
                    margin-bottom: 24px;
                }
                
                .welcome-avatar {
                    width: 36px;
                    height: 36px;
                    background: white;
                    border-radius: 10px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 16px;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
                }
                
                .welcome-text {
                    flex: 1;
                }
                
                .welcome-text strong {
                    display: block;
                    font-size: 14px;
                    margin-bottom: 4px;
                    color: #1f2937;
                }
                
                .welcome-text p {
                    margin: 0;
                    font-size: 13px;
                    color: #6b7280;
                    line-height: 1.4;
                }
                
                .quick-actions {
                    display: grid;
                    grid-template-columns: 1fr;
                    gap: 8px;
                    margin-bottom: 20px;
                }
                
                .action-card {
                    background: white;
                    border: 1px solid #e5e7eb;
                    border-radius: 12px;
                    padding: 16px;
                    cursor: pointer;
                    transition: all 0.3s ease;
                    display: flex;
                    align-items: center;
                    gap: 12px;
                }
                
                .action-card:hover {
                    background: #f8fafc;
                    border-color: #667eea;
                    transform: translateY(-2px);
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                }
                
                .action-icon {
                    width: 32px;
                    height: 32px;
                    background: #f3f4f6;
                    border-radius: 8px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 14px;
                }
                
                .action-card span {
                    font-size: 14px;
                    font-weight: 500;
                    color: #374151;
                }
                
                .view-header {
                    margin-bottom: 24px;
                }
                
                .view-header h3 {
                    margin: 0 0 8px 0;
                    font-size: 18px;
                    font-weight: 600;
                    color: #1f2937;
                }
                
                .view-header p {
                    margin: 0;
                    font-size: 14px;
                    color: #6b7280;
                    line-height: 1.4;
                }
                
                .sites-grid {
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 12px;
                }
                
                .site-card {
                    background: white;
                    border: 1px solid #e5e7eb;
                    border-radius: 12px;
                    padding: 16px;
                    cursor: pointer;
                    text-align: center;
                    transition: all 0.2s ease;
                    font-size: 14px;
                    font-weight: 500;
                    color: #374151;
                }
                
                .site-card:hover {
                    background: #f8fafc;
                    border-color: #667eea;
                    transform: translateY(-2px);
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                }
                
                .reference-section {
                    margin-top: 20px;
                }
                
                .input-group {
                    display: flex;
                    gap: 8px;
                    align-items: center;
                }
                
                #refCodeInput, #chatInput, #phoneInput {
                    flex: 1;
                    padding: 12px 16px;
                    border: 1px solid #e5e7eb;
                    border-radius: 12px;
                    font-size: 14px;
                    outline: none;
                    transition: all 0.2s ease;
                }
                
                #refCodeInput:focus, #chatInput:focus, #phoneInput:focus {
                    border-color: #667eea;
                    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
                }
                
                #searchRefBtn, #sendMessageBtn, #getAddressBtn {
                    width: 44px;
                    height: 44px;
                    background: #667eea;
                    border: none;
                    border-radius: 12px;
                    cursor: pointer;
                    color: white;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    transition: all 0.2s ease;
                }
                
                #searchRefBtn:hover, #sendMessageBtn:hover, #getAddressBtn:hover {
                    background: #5a6fd8;
                    transform: scale(1.05);
                }
                
                .messages-container {
                    flex: 1;
                    display: flex;
                    flex-direction: column;
                    gap: 12px;
                    margin-bottom: 16px;
                    max-height: 400px;
                    overflow-y: auto;
                }
                
                .message {
                    padding: 12px 16px;
                    border-radius: 12px;
                    font-size: 14px;
                    line-height: 1.4;
                    max-width: 85%;
                    word-wrap: break-word;
                }
                
                .message-bot {
                    background: white;
                    border: 1px solid #e5e7eb;
                    align-self: flex-start;
                    border-bottom-left-radius: 4px;
                }
                
                .message-user {
                    background: #667eea;
                    color: white;
                    align-self: flex-end;
                    border-bottom-right-radius: 4px;
                }
                
                .chat-input-container {
                    border-top: 1px solid #e5e7eb;
                    padding-top: 16px;
                    margin-top: auto;
                }
                
                .loading-state {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    padding: 40px 20px;
                    text-align: center;
                }
                
                .loading-spinner {
                    width: 32px;
                    height: 32px;
                    border: 3px solid #f3f4f6;
                    border-top: 3px solid #667eea;
                    border-radius: 50%;
                    animation: spin 1s linear infinite;
                    margin-bottom: 12px;
                }
                
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
                
                .loading-state p {
                    margin: 0;
                    color: #6b7280;
                    font-size: 14px;
                }
                
                /* Address View Stilleri */
                .address-section {
                    margin-top: 20px;
                }
                
                .address-result {
                    background: white;
                    border: 1px solid #e5e7eb;
                    border-radius: 12px;
                    padding: 16px;
                    margin-top: 16px;
                    font-size: 14px;
                    line-height: 1.5;
                }
                
                .address-line {
                    margin-bottom: 6px;
                    padding: 2px 0;
                }
            </style>
        `;
        
        document.head.insertAdjacentHTML('beforeend', styles);
    }
    
    attachEvents() {
        document.getElementById('shipliyoBubble').addEventListener('click', () => {
            this.toggleWidget();
        });
        
        document.querySelector('.close-btn').addEventListener('click', () => {
            this.closeWidget();
        });
        
        document.getElementById('backBtn').addEventListener('click', () => {
            this.goBack();
        });
        
        document.querySelectorAll('.action-card').forEach(card => {
            card.addEventListener('click', (e) => {
                const action = e.currentTarget.dataset.action;
                this.handleAction(action);
            });
        });
        
        document.getElementById('searchRefBtn').addEventListener('click', () => {
            this.searchReference();
        });
        
        document.getElementById('refCodeInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.searchReference();
            }
        });
        
        document.getElementById('sendMessageBtn').addEventListener('click', () => {
            this.sendMessage();
        });
        
        document.getElementById('chatInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });
        
        // Yeni adres butonu event'leri
        document.getElementById('getAddressBtn').addEventListener('click', () => {
            this.processPhoneNumber();
        });
        
        document.getElementById('phoneInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.processPhoneNumber();
            }
        });
        
        // ✅ DİL BUTONLARI EVENT'LERİ EKLENDİ
        document.querySelectorAll('.lang-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const lang = e.currentTarget.dataset.lang;
                this.setLanguage(lang);
                
                // Buton görünümünü güncelle
                document.querySelectorAll('.lang-btn').forEach(b => {
                    b.classList.remove('active');
                });
                e.currentTarget.classList.add('active');
            });
        });
    }
    
    toggleWidget() {
        this.isOpen = !this.isOpen;
        document.getElementById('shipliyoWindow').style.display = this.isOpen ? 'flex' : 'none';
        if (this.isOpen) {
            this.showView('main');
        }
    }
    
    closeWidget() {
        this.isOpen = false;
        document.getElementById('shipliyoWindow').style.display = 'none';
        this.viewHistory = [];
        this.updateBackButton();
    }
    
    showView(viewName, addToHistory = true) {
        // Tüm view'leri gizle
        document.querySelectorAll('[class^="view-"]').forEach(view => {
            view.style.display = 'none';
        });
        
        // İstenen view'i göster
        document.getElementById(viewName + 'View').style.display = 'block';
        this.currentView = viewName;
        
        // History'ye ekle (main view hariç)
        if (addToHistory && viewName !== 'main') {
            this.viewHistory.push(viewName);
        }
        
        this.updateBackButton();
    }
    
    goBack() {
        if (this.viewHistory.length > 0) {
            this.viewHistory.pop(); // Mevcut view'ı çıkar
            const previousView = this.viewHistory.length > 0 ? this.viewHistory[this.viewHistory.length - 1] : 'main';
            this.showView(previousView, false); // History'ye ekleme
        } else {
            this.showView('main');
        }
    }
    
    updateBackButton() {
        const backBtn = document.getElementById('backBtn');
        backBtn.style.display = this.viewHistory.length > 0 ? 'flex' : 'none';
    }
    
    handleAction(action) {
        console.log('Action:', action);
        switch(action) {
            case 'get_code':
                this.showSitesView();
                break;
            case 'help':
                this.showHelp();
                break;
            case 'reference_input':
                this.showReferenceView();
                break;
            case 'get_address':
                this.showAddressView();
                break;
        }
    }
    
    loadSites() {
        const sites = [
            { name: 'Trendyol', id: 'trendyol' },
            { name: 'Hepsiburada', id: 'hepsiburada' },
            { name: 'n11', id: 'n11' },
            { name: 'Diğer', id: 'other' }
        ];
        
        const grid = document.getElementById('sitesGrid');
        grid.innerHTML = '';
        
        sites.forEach(site => {
            const card = document.createElement('div');
            card.className = 'site-card';
            card.textContent = site.name;
            card.dataset.site = site.id;
            card.addEventListener('click', () => {
                this.selectSite(site.id);
            });
            grid.appendChild(card);
        });
    }
    
    showSitesView() {
        this.showView('sites');
    }
    
    showReferenceView() {
        this.showView('reference');
        document.getElementById('refCodeInput').focus();
    }
    
    showAddressView() {
        this.showView('address');
        document.getElementById('phoneInput').focus();
    }
    
    searchReference() {
        const refCode = document.getElementById('refCodeInput').value.trim();
        if (!refCode) return;
        
        this.showChatView();
        this.addMessage(refCode + " " + this.t('searching'), 'user');
        
        fetch(this.API_BASE_URL + '/api/chatbot', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                message: refCode,
                session_id: 'widget_user_' + Date.now(),
                language: this.currentLanguage
            })
        })
        .then(response => response.json())
        .then(data => {
            this.addMessage(data.response || this.t('noSms'), 'bot');
        })
        .catch(error => {
            this.addMessage(this.t('error') + ' ' + error.message, 'bot');
        });
    }
    
    processPhoneNumber() {
        const phoneInput = document.getElementById('phoneInput');
        const phoneNumber = phoneInput.value.trim();
        const resultDiv = document.getElementById('addressResult');
        
        if (!phoneNumber) return;
        
        if (phoneNumber.length === 9 && /^\d+$/.test(phoneNumber)) {
            const fullAddress = `BG${phoneNumber} Hatip Mahallesi Fulya Sokak No: 19/A Çorlu, Tekirdağ`;
            
            let addressHTML = `
                <div style="margin-bottom: 15px; font-weight: 600; color: #667eea;">${this.t('addressResult')}</div>
                <div style="margin-bottom: 10px; font-family: monospace; background: #f8f9fa; padding: 10px; border-radius: 8px;">${fullAddress}</div>
                
                <div style="margin-top: 15px; padding-top: 15px; border-top: 1px dashed #ddd;">
                    <div style="font-weight: 600; margin-bottom: 8px; color: #667eea;">${this.t('turkish')}</div>
                    <div>${this.t('city')} Tekirdağ</div>
                    <div>${this.t('district')} Çorlu</div>
                    <div>${this.t('neighborhood')} Hatip</div>
                    <div>${this.t('street')} Fulya</div>
                    <div>${this.t('buildingNo')} 19/A</div>
                </div>
                
                <div style="margin-top: 15px; padding-top: 15px; border-top: 1px dashed #ddd;">
                    <div style="font-weight: 600; margin-bottom: 8px; color: #667eea;">${this.t('english')}</div>
                    <div>${this.t('city')} Tekirdağ</div>
                    <div>${this.t('district')} Çorlu</div>
                    <div>${this.t('neighborhood')} Hatip</div>
                    <div>${this.t('street')} Fulya</div>
                    <div>${this.t('buildingNo')} 19/A</div>
                </div>
                
                <div style="margin-top: 15px; padding-top: 15px; border-top: 1px dashed #ddd;">
                    <div style="font-weight: 600; margin-bottom: 8px; color: #667eea;">${this.t('bulgarian')}</div>
                    <div>${this.t('city')} Tekirdağ</div>
                    <div>${this.t('district')} Çorlu</div>
                    <div>${this.t('neighborhood')} Hatip</div>
                    <div>${this.t('street')} Fulya</div>
                    <div>${this.t('buildingNo')} 19/A</div>
                </div>
            `;
            
            resultDiv.innerHTML = addressHTML;
            resultDiv.style.display = 'block';
        } else {
            resultDiv.innerHTML = '<div style="color: #ef4444;">' + this.t('invalidPhone') + '</div>';
            resultDiv.style.display = 'block';
        }
    }
    
    selectSite(site) {
        this.showChatView();
        this.addMessage(site + ' ' + this.t('searching'), 'user');
        
        fetch(this.API_BASE_URL + '/api/chatbot', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                message: site,
                session_id: 'widget_user_' + Date.now(),
                language: this.currentLanguage
            })
        })
        .then(response => response.json())
        .then(data => {
            this.showLoading(false);
            
            if (data.sms_list && data.sms_list.length > 0) {
                let message = this.t('smsFound') + ` ${data.sms_list.length} SMS:\n\n`;
                
                data.sms_list.forEach((sms, index) => {
                    let codeDisplay = sms.code;
                    if (!codeDisplay && sms.raw) {
                        const codeMatch = sms.raw.match(/\b\d{4,6}\b/);
                        codeDisplay = codeMatch ? codeMatch[0] : sms.raw;
                    }
                    
                    message += `${index + 1}. 📱 ${codeDisplay}\n`;
                });
                
                this.addMessage(message, 'bot');
            } else if (data.response) {
                this.addMessage(data.response, 'bot');
            } else {
                this.addMessage(this.t('noSms'), 'bot');
            }
        })
        .catch(error => {
            this.addMessage(this.t('error') + ' ' + error.message, 'bot');
        });
    }
    
    showHelp() {
        this.showChatView();
        this.addMessage(this.t('help'), 'user');
        
        this.addMessage('Shipliyo Asistan size şu konularda yardımcı olabilir:\n\n• Doğrulama kodlarınızı almak\n• SMS geçmişinizi görüntülemek\n• Site bazlı filtreleme yapmak\n• Referans kodları ile arama yapmak\n• Teslimat adresinizi almak\n\nBir site seçerek işleme başlayabilirsiniz.', 'bot');
    }
    
    showChatView() {
        this.showView('chat');
    }
    
    sendMessage() {
        const input = document.getElementById('chatInput');
        const message = input.value.trim();
        if (!message) return;
        
        this.addMessage(message, 'user');
        input.value = '';
        
        fetch(this.API_BASE_URL + '/api/chatbot', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                message: message,
                session_id: 'widget_user_' + Date.now(),
                language: this.currentLanguage
            })
        })
        .then(response => response.json())
        .then(data => {
            this.addMessage(data.response || 'Anladım', 'bot');
        })
        .catch(error => {
            this.addMessage(this.t('error') + ' ' + error.message, 'bot');
        });
    }
    
    addMessage(text, sender) {
        const container = document.getElementById('messagesContainer');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message message-${sender}`;
        
        const formattedText = text.replace(/\n/g, '<br>');
        messageDiv.innerHTML = formattedText;
        
        container.appendChild(messageDiv);
        container.scrollTop = container.scrollHeight;
    }
    
    showLoading(show) {
        document.getElementById('loadingState').style.display = show ? 'flex' : 'none';
    }
}

window.addEventListener('DOMContentLoaded', () => {
    window.shipliyoWidget = new ShipliyoWidget();
});