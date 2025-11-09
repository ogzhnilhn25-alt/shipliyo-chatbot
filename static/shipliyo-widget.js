// Shipliyo Chat Widget - Premium Tasarım
class ShipliyoWidget {
    constructor() {
        this.isOpen = false;
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
                        </div>
                        
                        <div class="reference-section" id="referenceSection">
                            <div class="input-group">
                                <input type="text" id="refCodeInput" placeholder="A1B2C3">
                                <button id="searchRefBtn">
                                    <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                                        <path d="M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001c.03.04.062.078.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1.007 1.007 0 0 0-.115-.1zM12 6.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0z"/>
                                    </svg>
                                </button>
                            </div>
                        </div>
                        
                        <div class="sites-grid" id="sitesGrid"></div>
                        
                        <div class="messages-container" id="messagesContainer"></div>
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
                
                #refCodeInput {
                    flex: 1;
                    padding: 12px 16px;
                    border: 1px solid #e5e7eb;
                    border-radius: 12px;
                    font-size: 14px;
                    outline: none;
                    transition: all 0.2s ease;
                }
                
                #refCodeInput:focus {
                    border-color: #667eea;
                    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
                }
                
                #searchRefBtn {
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
                
                #searchRefBtn:hover {
                    background: #5a6fd8;
                    transform: scale(1.05);
                }
                
                .sites-grid {
                    display: none;
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
                }
                
                .site-card:hover {
                    background: #f8fafc;
                    border-color: #667eea;
                    transform: translateY(-1px);
                }
                
                .messages-container {
                    display: flex;
                    flex-direction: column;
                    gap: 8px;
                }
                
                .message {
                    padding: 12px 16px;
                    border-radius: 12px;
                    font-size: 14px;
                    line-height: 1.4;
                    max-width: 85%;
                }
                
                .message-bot {
                    background: white;
                    border: 1px solid #e5e7eb;
                    align-self: flex-start;
                }
                
                .message-user {
                    background: #667eea;
                    color: white;
                    align-self: flex-end;
                }
            </style>
        `;
        
        document.head.insertAdjacentHTML('beforeend', styles);
    }
    
    // ... (diğer metodlar aynı kalacak, sadece tasarım değişti)
}

// Widget'ı başlat
if (typeof window !== 'undefined') {
    document.addEventListener('DOMContentLoaded', function() {
        new ShipliyoWidget();
    });
}