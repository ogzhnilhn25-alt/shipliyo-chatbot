// Shipliyo Chat Widget - Premium Tasarım (Güncellenmiş)
class ShipliyoWidget {
    constructor() {
        this.isOpen = false;
        this.isLoading = false;
        this.currentView = 'main'; // main, chat, sites
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
                
                .reference-section {
                    display: none;
                    margin-bottom: 20px;
                }
                
                .input-group {
                    display: flex;
                    gap: 8px;
                    align-items: center;
                }
                
                #refCodeInput, #chatInput {
                    flex: 1;
                    padding: 12px 16px;
                    border: 1px solid #e5e7eb;
                    border-radius: 12px;
                    font-size: 14px;
                    outline: none;
                    transition: all 0.2s ease;
                }
                
                #refCodeInput:focus, #chatInput:focus {
                    border-color: #667eea;
                    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
                }
                
                #searchRefBtn, #sendMessageBtn {
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
                
                #searchRefBtn:hover, #sendMessageBtn:hover {
                    background: #5a6fd8;
                    transform: scale(1.05);
                }
                
                .sites-grid {
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 8px;
                    margin-bottom: 20px;
                }
                
                .site-card {
                    background: white;
                    border: 1px solid #e5e7eb;
                    border-radius: 12px;
                    padding: 12px;
                    cursor: pointer;
                    text-align: center;
                    transition: all 0.2s ease;
                    font-size: 12px;
                    font-weight: 500;
                    color: #374151;
                    text-decoration: none;
                    display: block;
                }
                
                .site-card:hover {
                    background: #f8fafc;
                    border-color: #667eea;
                    transform: translateY(-1px);
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
            </style>
        `;
        
        document.head.insertAdjacentHTML('beforeend', styles);
    }
    
    attachEvents() {
        // Bubble click
        document.getElementById('shipliyoBubble').addEventListener('click', () => {
            this.toggleWidget();
        });
        
        // Close button
        document.querySelector('.close-btn').addEventListener('click', () => {
            this.closeWidget();
        });
        
        // Action cards
        document.querySelectorAll('.action-card').forEach(card => {
            card.addEventListener('click', (e) => {
                const action = e.currentTarget.dataset.action;
                this.handleAction(action);
            });
        });
        
        // Reference search
        document.getElementById('searchRefBtn').addEventListener('click', () => {
            this.searchReference();
        });
        
        document.getElementById('refCodeInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.searchReference();
            }
        });
        
        // Chat input
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
        // Hide all views
        document.querySelectorAll('[class^="view-"]').forEach(view => {
            view.style.display = 'none';
        });
        
        // Show selected view
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
        
        // Backend API call simulation
        setTimeout(() => {
            this.showLoading(false);
            this.addMessage(`"${refCode}" referans kodu için arama yapılıyor...`, 'bot');
            // Burada backend API'ye istek atılacak
        }, 1000);
    }
    
    showSites() {
        this.showView('main');
        document.getElementById('sitesGrid').style.display = 'grid';
    }
    
    loadSites() {
        // Boş sites array - kendi sitelerini buraya ekleyebilirsin
        const sites = [
            // Örnek: { name: 'Site Adı', url: 'https://site.com', icon: '🌐' }
        ];
        
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
        
        // Backend API call simulation
        setTimeout(() => {
            this.showLoading(false);
            this.addMessage('Doğrulama kodunuz: 123456', 'bot');
            this.showView('chat');
        }, 1500);
    }
    
    showHelp() {
        this.showView('chat');
        this.addMessage('Size nasıl yardımcı olabilirim? Aşağıdaki konularda destek sunuyorum:\n\n• Doğrulama kodları\n• Referans aramaları\n• Sistem entegrasyonları\n• Genel sorular', 'bot');
    }
    
    sendMessage() {
        const input = document.getElementById('chatInput');
        const message = input.value.trim();
        
        if (!message) return;
        
        this.addMessage(message, 'user');
        input.value = '';
        
        // Simulate AI response
        setTimeout(() => {
            this.addMessage('Mesajınızı aldım. Size en kısa sürede yardımcı olacağım!', 'bot');
        }, 1000);
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

// Widget'ı başlat
if (typeof window !== 'undefined') {
    document.addEventListener('DOMContentLoaded', function() {
        window.shipliyoWidget = new ShipliyoWidget();
    });
}