// Shipliyo Chat Widget
class ShipliyoWidget {
    constructor() {
        this.isOpen = false;
        this.init();
    }
    
    init() {
        // Widget'ı oluştur
        this.createWidget();
        // Event listener'ları ekle
        this.attachEvents();
    }
    
    createWidget() {
        const widgetHTML = `
            <div id="shipliyoWidget">
                <!-- Chat Bubble -->
                <div id="shipliyoBubble">
                    <span>💬</span>
                </div>
                
                <!-- Chat Window -->
                <div id="shipliyoWindow">
                    <!-- Header -->
                    <div class="widget-header">
                        <div class="header-content">
                            <h3>🤖 Shipliyo Asistan</h3>
                            <small>Size nasıl yardımcı olabilirim?</small>
                        </div>
                        <button class="close-btn">×</button>
                    </div>
                    
                    <!-- Body -->
                    <div class="widget-body">
                        <div class="welcome-message">
                            Hoş geldiniz! Aşağıdaki seçeneklerden birini seçin:
                        </div>
                        
                        <div class="bubbles-container">
                            <div class="bubble" data-action="get_code">
                                <span class="bubble-icon">📱</span>
                                <span>Doğrulama Kodu Al</span>
                            </div>
                            
                            <div class="bubble" data-action="help">
                                <span class="bubble-icon">❓</span>
                                <span>Yardım & Bilgi</span>
                            </div>
                            
                            <div class="bubble" data-action="reference_input">
                                <span class="bubble-icon">🔍</span>
                                <span>Referans Kodu ile Ara</span>
                            </div>
                        </div>
                        
                        <!-- Referans Input -->
                        <div class="reference-input" id="referenceInput">
                            <input type="text" id="refCodeInput" placeholder="Referans kodunu girin (örn: A1B2C3)">
                            <button id="searchRefBtn">🔍 Ara</button>
                        </div>
                        
                        <!-- Site Seçim -->
                        <div class="site-bubbles" id="siteBubbles"></div>
                        
                        <!-- Yanıt Alanı -->
                        <div class="response-area" id="responseArea"></div>
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
                    bottom: 20px;
                    right: 20px;
                    z-index: 10000;
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                }
                
                #shipliyoBubble {
                    width: 60px;
                    height: 60px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    cursor: pointer;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.2);
                    transition: all 0.3s ease;
                    font-size: 24px;
                    color: white;
                }
                
                #shipliyoBubble:hover {
                    transform: scale(1.1);
                    box-shadow: 0 6px 25px rgba(0,0,0,0.3);
                }
                
                #shipliyoWindow {
                    position: absolute;
                    bottom: 70px;
                    right: 0;
                    width: 380px;
                    height: 520px;
                    background: white;
                    border-radius: 15px;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                    display: none;
                    flex-direction: column;
                    overflow: hidden;
                }
                
                .widget-header {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 15px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }
                
                .header-content h3 {
                    margin: 0 0 5px 0;
                    font-size: 18px;
                }
                
                .header-content small {
                    opacity: 0.9;
                    font-size: 12px;
                }
                
                .close-btn {
                    background: none;
                    border: none;
                    color: white;
                    font-size: 24px;
                    cursor: pointer;
                    padding: 0;
                    width: 30px;
                    height: 30px;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                
                .close-btn:hover {
                    background: rgba(255,255,255,0.2);
                }
                
                .widget-body {
                    flex: 1;
                    padding: 20px;
                    overflow-y: auto;
                    background: #f8f9fa;
                }
                
                .welcome-message {
                    text-align: center;
                    color: #666;
                    margin-bottom: 20px;
                    font-size: 14px;
                }
                
                .bubbles-container {
                    display: flex;
                    flex-direction: column;
                    gap: 10px;
                }
                
                .bubble {
                    background: white;
                    border: 2px solid #e9ecef;
                    border-radius: 12px;
                    padding: 12px 15px;
                    cursor: pointer;
                    transition: all 0.3s ease;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                    font-size: 14px;
                    font-weight: 500;
                }
                
                .bubble:hover {
                    background: #007bff;
                    color: white;
                    border-color: #007bff;
                    transform: translateY(-1px);
                }
                
                .bubble-icon {
                    font-size: 16px;
                }
                
                .reference-input {
                    display: none;
                    margin-top: 15px;
                    gap: 10px;
                }
                
                #refCodeInput {
                    flex: 1;
                    padding: 10px 15px;
                    border: 2px solid #e9ecef;
                    border-radius: 25px;
                    font-size: 14px;
                    outline: none;
                }
                
                #refCodeInput:focus {
                    border-color: #007bff;
                }
                
                #searchRefBtn {
                    padding: 10px 20px;
                    background: #007bff;
                    color: white;
                    border: none;
                    border-radius: 25px;
                    cursor: pointer;
                    font-size: 14px;
                }
                
                #searchRefBtn:hover {
                    background: #0056b3;
                }
                
                .site-bubbles {
                    display: none;
                    flex-wrap: wrap;
                    gap: 8px;
                    margin-top: 15px;
                }
                
                .site-bubble {
                    background: #28a745;
                    color: white;
                    border: none;
                    border-radius: 20px;
                    padding: 8px 12px;
                    cursor: pointer;
                    font-size: 12px;
                    transition: all 0.3s ease;
                }
                
                .site-bubble:hover {
                    background: #218838;
                    transform: scale(1.05);
                }
                
                .response-area {
                    margin-top: 15px;
                }
                
                .response-message {
                    background: white;
                    border-radius: 12px;
                    padding: 12px 15px;
                    margin: 8px 0;
                    font-size: 14px;
                    line-height: 1.4;
                    border-left: 4px solid #007bff;
                }
            </style>
        `;
        
        document.head.insertAdjacentHTML('beforeend', styles);
    }
    
    attachEvents() {
        const bubble = document.getElementById('shipliyoBubble');
        const window = document.getElementById('shipliyoWindow');
        const closeBtn = document.querySelector('.close-btn');
        
        // Aç/kapa
        bubble.addEventListener('click', () => this.toggleWindow());
        closeBtn.addEventListener('click', () => this.closeWindow());
        
        // Baloncuk tıklamaları
        document.addEventListener('click', (e) => {
            if (e.target.closest('.bubble')) {
                const bubbleEl = e.target.closest('.bubble');
                const action = bubbleEl.getAttribute('data-action');
                this.handleBubbleClick(action);
            }
            
            if (e.target.closest('.site-bubble')) {
                const siteBubble = e.target.closest('.site-bubble');
                const site = siteBubble.getAttribute('data-site');
                this.sendMessage(site);
            }
        });
        
        // Referans arama
        document.getElementById('searchRefBtn').addEventListener('click', () => this.searchByReference());
        document.getElementById('refCodeInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.searchByReference();
        });
        
        // Dışarı tıklayınca kapat
        document.addEventListener('click', (e) => {
            if (!e.target.closest('#shipliyoWidget') && this.isOpen) {
                this.closeWindow();
            }
        });
    }
    
    toggleWindow() {
        const window = document.getElementById('shipliyoWindow');
        this.isOpen = !this.isOpen;
        window.style.display = this.isOpen ? 'flex' : 'none';
    }
    
    closeWindow() {
        const window = document.getElementById('shipliyoWindow');
        this.isOpen = false;
        window.style.display = 'none';
        this.resetToMainMenu();
    }
    
    handleBubbleClick(action) {
        if (action === 'reference_input') {
            this.showReferenceInput();
        } else {
            this.sendMessage(action);
        }
    }
    
    showReferenceInput() {
        document.getElementById('referenceInput').style.display = 'flex';
        document.getElementById('siteBubbles').style.display = 'none';
    }
    
    searchByReference() {
        const refCode = document.getElementById('refCodeInput').value.trim();
        if (refCode) {
            this.sendMessage(refCode);
            document.getElementById('refCodeInput').value = '';
            document.getElementById('referenceInput').style.display = 'none';
        }
    }
    
    async sendMessage(message) {
        try {
            const response = await fetch('/api/chatbot', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    message: message,
                    session_id: 'widget_user_' + Date.now(),
                    language: 'tr'
                })
            });
            
            const data = await response.json();
            this.handleResponse(data);
            
        } catch (error) {
            this.showResponse('⚠️ Bir hata oluştu: ' + error.message);
        }
    }
    
    handleResponse(data) {
        // Site seçim baloncukları
        if (data.bubbles && data.bubbles[0] && data.bubbles[0].payload === 'trendyol') {
            this.showSiteBubbles(data.bubbles);
        } 
        // Ana menü baloncukları
        else if (data.bubbles) {
            this.updateBubbles(data.bubbles);
        }
        
        // Yanıtı göster
        if (data.response) {
            this.showResponse(data.response);
        }
    }
    
    updateBubbles(bubbles) {
        const container = document.querySelector('.bubbles-container');
        let bubblesHtml = '';
        
        bubbles.forEach(bubble => {
            const icon = bubble.title.includes('Kod') ? '📱' : 
                        bubble.title.includes('Yardım') ? '❓' : '💬';
            
            bubblesHtml += `
                <div class="bubble" data-action="${bubble.payload}">
                    <span class="bubble-icon">${icon}</span>
                    <span>${bubble.title}</span>
                </div>
            `;
        });
        
        container.innerHTML = bubblesHtml;
        this.hideReferenceInput();
        this.hideSiteBubbles();
    }
    
    showSiteBubbles(bubbles) {
        const container = document.getElementById('siteBubbles');
        let bubblesHtml = '';
        
        bubbles.forEach(bubble => {
            bubblesHtml += `<button class="site-bubble" data-site="${bubble.payload}">${bubble.title}</button>`;
        });
        
        container.innerHTML = bubblesHtml;
        container.style.display = 'flex';
        this.showResponse('Hangi siteden kod almak istiyorsunuz?');
    }
    
    hideReferenceInput() {
        document.getElementById('referenceInput').style.display = 'none';
    }
    
    hideSiteBubbles() {
        document.getElementById('siteBubbles').style.display = 'none';
    }
    
    showResponse(text) {
        const responseArea = document.getElementById('responseArea');
        const responseDiv = document.createElement('div');
        responseDiv.className = 'response-message';
        responseDiv.textContent = text;
        responseArea.appendChild(responseDiv);
        
        // Otomatik kaydırma
        responseArea.scrollTop = responseArea.scrollHeight;
    }
    
    resetToMainMenu() {
        this.hideReferenceInput();
        this.hideSiteBubbles();
        document.getElementById('responseArea').innerHTML = '';
    }
}

// Widget'ı başlat
if (typeof window !== 'undefined') {
    document.addEventListener('DOMContentLoaded', function() {
        new ShipliyoWidget();
    });
}