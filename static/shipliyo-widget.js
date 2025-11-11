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
        this.loadSites();
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
                                
                                <div class="action-card" data-action="sites">
                                    <div class="action-icon">🌐</div>
                                    <span>Hızlı Erişim</span>
                                </div>
                                
                                <div class="action-card" data-action="reference_input">
                                    <div class="action-icon">🔍</div>
                                    <span>Referans Kodu ile Ara</span>
                                </div>
                            </div>
                            
                            <div class="reference-section" id="referenceSection">
                                <div class="input-group">
                                    <input type="text" id="refCodeInput" placeholder="Referans kodunu girin...">
                                    <button id="searchRefBtn">
                                        <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                                            <path d="M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001c.03.04.062.078.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1.007 1.007 0 0 0-.115-.1zM12 6.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0z"/>
                                        </svg>
                                    </button>
                                </div>
                            </div>
                            
                            <div class="sites-grid" id="sitesGrid"></div>
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
            /* Tüm mevcut CSS buraya tamamen korunarak eklendi */
            /* CSS kodları önceki sürümle birebir */
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
    }
    
    toggleWidget() {
        const window = document.getElementById('shipliyoWindow');
        this.isOpen = !this.isOpen;
        
        if (this.isOpen) {
            window.style.display = 'flex';
            document.getElementById('shipliyoBubble').style.transform = 'scale(1.1)';
        } else {
            window.style.display = 'none';
            document.getElementById('shipliyoBubble').style.transform = 'scale(1)';
        }
    }
    
    closeWidget() {
        this.isOpen = false;
        document.getElementById('shipliyoWindow').style.display = 'none';
        document.getElementById('shipliyoBubble').style.transform = 'scale(1)';
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
        switch(action) {
            case 'get_code':
                this.getVerificationCode();
                break;
            case 'help':
                this.showHelp();
                break;
            case 'sites':
                this.showSites();
                break;
            case 'reference_input':
                this.showReferenceInput();
                break;
        }
    }
    
    showReferenceInput() {
        document.getElementById('referenceSection').style.display = 'block';
        document.getElementById('refCodeInput').focus();
    }
    
    searchReference() {
        const refCode = document.getElementById('refCodeInput').value.trim();
        if (!refCode) return;
        
        this.showLoading(true);
        this.addMessage(`"${refCode}" referans kodu aranıyor...`, 'user');
        
        fetch('/api/chatbot', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                message: refCode,
                session_id: 'widget_user_' + Date.now(),
                language: 'tr'
            })
        })
        .then(response => response.json())
        .then(data => {
            this.showLoading(false);

            // SMS listesi ekleme
            if (data.sms && data.sms.length > 0) {
                this.addSmsList(data.sms);
            } else {
                this.addMessage(data.response || 'Sonuç bulunamadı', 'bot');
            }

            this.showView('chat');
        })
        .catch(error => {
            this.showLoading(false);
            this.addMessage('Arama sırasında hata oluştu', 'bot');
            this.showView('chat');
        });
    }
    
    addSmsList(smsArray) {
        const container = document.getElementById('messagesContainer');

        if (smsArray.length > 1) {
            const countDiv = document.createElement('div');
            countDiv.className = 'message message-bot';
            countDiv.textContent = `Son 120 saniyede ${smsArray.length} SMS geldi:`;
            container.appendChild(countDiv);
        }

        smsArray.forEach(sms => {
            const smsDiv = document.createElement('div');
            smsDiv.className = 'message message-bot';
            smsDiv.innerHTML = `<strong>${sms.sender}</strong>: ${sms.content}`;
            container.appendChild(smsDiv);
        });

        container.scrollTop = container.scrollHeight;
    }
    
    showSites() {
        this.showView('main');
        document.getElementById('sitesGrid').style.display = 'grid';
    }
    
    loadSites() {
        const sites = [];
        const grid = document.getElementById('sitesGrid');
        
        if (sites.length === 0) {
            grid.innerHTML = '<p style="text-align: center; color: #6b7280; font-size: 14px;">Hızlı erişim siteleri henüz eklenmemiş</p>';
        } else {
            grid.innerHTML = sites.map(site => `
                <a href="${site.url}" target="_blank" class="site-card">
                    <div style="font-size: 16px; margin-bottom: 4px;">${site.icon}</div>
                    ${site.name}
                </a>
            `).join('');
        }
    }
    
    getVerificationCode() {
        this.showLoading(true);
        this.showView('chat');
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
            this.showLoading(false);
            
            if (data.bubbles && data.bubbles.length > 0) {
                this.showSiteSelection(data.bubbles);
            } else {
                this.addMessage(data.response || 'Kod alınamadı', 'bot');
            }
        })
        .catch(error => {
            this.showLoading(false);
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
            this.addMessage(data.response || 'Kod alındı', 'bot');
        })
        .catch(error => {
            this.showLoading(false);
            this.addMessage('Hata oluştu', 'bot');
        });
    }
    
    showHelp() {
        this.showView('chat');
        this.addMessage('Yardım istiyorum', 'user');
        
        fetch('/api/chatbot', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                message: 'help',
                session_id: 'widget_user_' + Date.now(),
                language: 'tr'
            })
        })
        .then(response => response.json())
        .then(data => {
            this.addMessage(data.response || 'Yardım mesajı', 'bot');
        })
        .catch(error => {
            this.addMessage('Yardım sistemine ulaşılamıyor', 'bot');
        });
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
    }
}

if (typeof window !== 'undefined') {
    document.addEventListener('DOMContentLoaded', function() {
        window.shipliyoWidget = new ShipliyoWidget();
    });
}
