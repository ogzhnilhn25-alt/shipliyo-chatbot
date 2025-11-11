// Shipliyo Chat Widget - Backend Entegreli
class ShipliyoWidget {
    constructor() {
        this.isOpen = false;
        this.isLoading = false;
        this.currentView = 'main';
        this.init();
    }
    
    init() {
        this.createWidget();
        this.attachEvents();
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
                            <div class="avatar">🤖</div>
                            <div class="header-text">
                                <h3>Shipliyo Asistan</h3>
                                <div class="status">
                                    <span class="status-dot"></span>
                                    <small>Çevrimiçi</small>
                                </div>
                            </div>
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
                    padding: 20px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }
                
                .header-content {
                    display: flex;
                    align-items: center;
                    gap: 12px;
                }
                
                .avatar {
                    width: 40px;
                    height: 40px;
                    background: rgba(255, 255, 255, 0.2);
                    border-radius: 12px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 18px;
                }
                
                .header-text h3 {
                    margin: 0 0 4px 0;
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
                    border-radius: 10px;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    transition: all 0.2s ease;
                }
                
                .close-btn:hover {
                    background: rgba(255, 255, 255, 0.3);
                    transform: rotate(90deg);
                }
                
                .widget-body {
                    flex: 1;
                    padding: 20px;
                    overflow-y: auto;
                    background: #fafbfc;
                    position: relative;
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
                
                .site-option {
                    cursor: pointer !important;
                    background: #f0f4ff !important;
                    border: 1px solid #667eea !important;
                    transition: all 0.2s ease;
                }
                
                .site-option:hover {
                    background: #e0e7ff !important;
                    transform: translateX(5px);
                }
                
                .chat-input-container {
                    border-top: 1px solid #e5e7eb;
                    padding-top: 16px;
                    margin-top: auto;
                }
                
                .input-group {
                    display: flex;
                    gap: 8px;
                    align-items: center;
                }
                
                #chatInput {
                    flex: 1;
                    padding: 12px 16px;
                    border: 1px solid #e5e7eb;
                    border-radius: 12px;
                    font-size: 14px;
                    outline: none;
                    transition: all 0.2s ease;
                }
                
                #chatInput:focus {
                    border-color: #667eea;
                    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
                }
                
                #sendMessageBtn {
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
                
                #sendMessageBtn:hover {
                    background: #5a6fd8;
                    transform: scale(1.05);
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
        
        document.querySelectorAll('.action-card').forEach(card => {
            card.addEventListener('click', (e) => {
                const action = e.currentTarget.dataset.action;
                this.handleAction(action);
            });
        });
        
        document.getElementById('sendMessageBtn').addEventListener('click', () => {
            this.sendMessage();
        });
        
        document.getElementById('chatInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });
    }
    
    toggleWidget() {
        this.isOpen = !this.isOpen;
        document.getElementById('shipliyoWindow').style.display = this.isOpen ? 'flex' : 'none';
    }
    
    closeWidget() {
        this.isOpen = false;
        document.getElementById('shipliyoWindow').style.display = 'none';
        this.showView('main');
    }
    
    showView(viewName) {
        document.querySelectorAll('[class^="view-"]').forEach(view => {
            view.style.display = 'none';
        });
        document.getElementById(viewName + 'View').style.display = 'block';
        this.currentView = viewName;
    }
    
    handleAction(action) {
        console.log('Action:', action);
        if (action === 'get_code') {
            this.getVerificationCode();
        } else if (action === 'help') {
            this.showHelp();
        }
    }
    
    getVerificationCode() {
        this.showChatView();
        this.addMessage('Doğrulama kodu istiyorum', 'user');
        
        fetch('/api/chatbot', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                message: 'get_code',
                session_id: 'widget_user_' + Date.now(),
                language: 'tr'
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.bubbles && data.bubbles.length > 0) {
                this.showSiteSelection(data.bubbles);
            } else {
                this.addMessage(data.response || 'Kod alınamadı', 'bot');
            }
        })
        .catch(error => {
            this.addMessage('Bağlantı hatası, lütfen tekrar deneyin.', 'bot');
        });
    }
    
    showSiteSelection(bubbles) {
        const container = document.getElementById('messagesContainer');
        this.addMessage('Hangi site için kod istiyorsunuz?', 'bot');
        
        bubbles.forEach(bubble => {
            const siteButton = document.createElement('div');
            siteButton.className = 'message message-bot site-option';
            siteButton.innerHTML = `<strong>${bubble.title}</strong>`;
            siteButton.addEventListener('click', () => {
                this.selectSite(bubble.payload);
            });
            container.appendChild(siteButton);
        });
        container.scrollTop = container.scrollHeight;
    }
    
    selectSite(sitePayload) {
        this.showLoading(true);
        this.addMessage(sitePayload, 'user');
        
        fetch('/api/chatbot', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                message: sitePayload,
                session_id: 'widget_user_' + Date.now(),
                language: 'tr'
            })
        })
        .then(response => response.json())
        .then(data => {
            this.showLoading(false);
            
            // SMS LİSTELEME - TÜM SMS'LERİ GÖSTER
            if (data.sms_list && data.sms_list.length > 0) {
                let message = `Son 120 saniyede ${data.sms_list.length} adet SMS bulundu:\n\n`;
                
                data.sms_list.forEach((sms, index) => {
                    // NULL KONTROLÜ - code null ise raw içeriğini göster
                    const codeDisplay = (sms.code && sms.code !== 'null') ? sms.code : (sms.raw || 'Kod bulunamadı');
                    message += `${index + 1}. 📱 Doğrulama Kodu: ${codeDisplay}\n`;
                    message += `   🌐 Site: ${sms.site}\n\n`;
                });
                
                this.addMessage(message, 'bot');
            } else if (data.response) {
                this.addMessage(data.response, 'bot');
            } else {
                this.addMessage('SMS bulunamadı.', 'bot');
            }
        })
        .catch(error => {
            this.showLoading(false);
            this.addMessage('Hata oluştu: ' + error.message, 'bot');
        });
    }
    
    showHelp() {
        this.showChatView();
        this.addMessage('Yardım istiyorum', 'user');
        
        this.addMessage('Shipliyo Asistan size şu konularda yardımcı olabilir:\n\n• Doğrulama kodlarınızı almak\n• SMS geçmişinizi görüntülemek\n• Site bazlı filtreleme yapmak\n\nBir site seçerek işleme başlayabilirsiniz.', 'bot');
    }
    
    showChatView() {
        this.currentView = 'chat';
        document.getElementById('mainView').style.display = 'none';
        document.getElementById('chatView').style.display = 'block';
    }
    
    sendMessage() {
        const input = document.getElementById('chatInput');
        const message = input.value.trim();
        if (!message) return;
        
        this.addMessage(message, 'user');
        input.value = '';
        
        fetch('/api/chatbot', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                message: message,
                session_id: 'widget_user_' + Date.now(),
                language: 'tr'
            })
        })
        .then(response => response.json())
        .then(data => {
            this.addMessage(data.response || 'Anladım', 'bot');
        })
        .catch(error => {
            this.addMessage('Mesajınız iletilemedi', 'bot');
        });
    }
    
    addMessage(text, sender) {
        const container = document.getElementById('messagesContainer');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message message-${sender}`;
        messageDiv.textContent = text;
        container.appendChild(messageDiv);
        container.scrollTop = container.scrollHeight;
    }
    
    showLoading(show) {
        document.getElementById('loadingState').style.display = show ? 'flex' : 'none';
        document.getElementById('mainView').style.display = show ? 'none' : 'block';
        document.getElementById('chatView').style.display = show ? 'none' : (this.currentView === 'chat' ? 'block' : 'none');
    }
}

window.addEventListener('DOMContentLoaded', () => {
    window.shipliyoWidget = new ShipliyoWidget();
});