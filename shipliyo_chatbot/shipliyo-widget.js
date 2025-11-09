// shipliyo-widget.js - PRODUCTION VERSION
(function() {
    'use strict';

    // PRODUCTION CONFIGURATION
    const defaultConfig = {
        apiUrl: 'https://api.shipliyo.com/api/chatbot',
        position: 'bottom-right',
        theme: 'light',
        language: 'tr',
        autoOpen: false
    };

    // Merge user config with defaults
    const config = {...defaultConfig, ...window.ShipliyoWidgetConfig};

    // Widget State
    let isOpen = false;
    let sessionId = 'widget_' + Math.random().toString(36).substr(2, 9);

    // Create Widget HTML
    function createWidget() {
        const widgetHTML = `
            <div id="shipliyo-chatbot-widget" style="
                position: fixed;
                ${config.position === 'bottom-right' ? 'right: 20px;' : 'left: 20px;'}
                bottom: 20px;
                width: 380px;
                height: 550px;
                background: white;
                border-radius: 20px;
                box-shadow: 0 15px 40px rgba(0,0,0,0.15);
                z-index: 10000;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
                display: none;
                flex-direction: column;
                border: 1px solid #e1e5e9;
                overflow: hidden;
            ">
                <!-- Header -->
                <div style="
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 20px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    flex-shrink: 0;
                ">
                    <div style="flex: 1;">
                        <div style="font-weight: 700; font-size: 18px; margin-bottom: 4px;">🤖 Shipliyo Asistan</div>
                        <div style="font-size: 12px; opacity: 0.9;">SMS Onay Kodları</div>
                    </div>
                    <button id="shipliyo-close-btn" style="
                        background: rgba(255,255,255,0.2);
                        border: none;
                        color: white;
                        width: 32px;
                        height: 32px;
                        border-radius: 50%;
                        cursor: pointer;
                        font-size: 18px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        transition: all 0.2s ease;
                    ">×</button>
                </div>

                <!-- Chat Messages -->
                <div id="shipliyo-chat-messages" style="
                    flex: 1;
                    padding: 20px;
                    overflow-y: auto;
                    background: #f8f9fa;
                    display: flex;
                    flex-direction: column;
                    gap: 12px;
                "></div>

                <!-- Input Area -->
                <div style="
                    padding: 20px;
                    border-top: 1px solid #e1e5e9;
                    background: white;
                    flex-shrink: 0;
                ">
                    <div style="display: flex; gap: 10px; align-items: center;">
                        <input type="text" id="shipliyo-message-input" 
                            placeholder="Mesajınızı yazın..." style="
                                flex: 1;
                                padding: 12px 16px;
                                border: 1px solid #e1e5e9;
                                border-radius: 25px;
                                outline: none;
                                font-size: 14px;
                            ">
                        <button id="shipliyo-send-btn" style="
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            color: white;
                            border: none;
                            width: 44px;
                            height: 44px;
                            border-radius: 50%;
                            cursor: pointer;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            font-size: 18px;
                        ">➤</button>
                    </div>
                </div>
            </div>

            <!-- Floating Button -->
            <div id="shipliyo-chat-button" style="
                position: fixed;
                ${config.position === 'bottom-right' ? 'right: 20px;' : 'left: 20px;'}
                bottom: 20px;
                width: 60px;
                height: 60px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-size: 24px;
                cursor: pointer;
                box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
                z-index: 9999;
            ">💬</div>
        `;

        document.body.insertAdjacentHTML('beforeend', widgetHTML);
        attachEventListeners();
    }

    // Event Listeners
    function attachEventListeners() {
        document.getElementById('shipliyo-chat-button').addEventListener('click', toggleWidget);
        document.getElementById('shipliyo-close-btn').addEventListener('click', toggleWidget);
        document.getElementById('shipliyo-send-btn').addEventListener('click', sendMessage);
        
        document.getElementById('shipliyo-message-input').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') sendMessage();
        });

        // Auto welcome message
        setTimeout(() => {
            if (!isOpen) {
                addMessage('🤖 Shipliyo Asistan hazır!', false, [
                    {title: '📱 Kod Al', payload: 'get_code'},
                    {title: '❓ Yardım', payload: 'help'}
                ]);
            }
        }, 3000);
    }

    // Toggle Widget
    function toggleWidget() {
        const widget = document.getElementById('shipliyo-chatbot-widget');
        const button = document.getElementById('shipliyo-chat-button');
        
        if (isOpen) {
            widget.style.display = 'none';
            button.style.display = 'flex';
            isOpen = false;
        } else {
            widget.style.display = 'flex';
            button.style.display = 'none';
            isOpen = true;
            
            if (document.getElementById('shipliyo-chat-messages').children.length === 0) {
                sendToBot('');
            }
            
            setTimeout(() => {
                document.getElementById('shipliyo-message-input').focus();
            }, 100);
        }
    }

    // Add Message
    function addMessage(message, isUser = false, bubbles = null) {
        const chatMessages = document.getElementById('shipliyo-chat-messages');
        
        const messageDiv = document.createElement('div');
        messageDiv.style.cssText = `
            display: flex;
            justify-content: ${isUser ? 'flex-end' : 'flex-start'};
            align-items: flex-end;
            gap: 8px;
        `;

        const bubbleDiv = document.createElement('div');
        bubbleDiv.style.cssText = `
            max-width: 85%;
            padding: 12px 16px;
            border-radius: 18px;
            background: ${isUser ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' : 'white'};
            color: ${isUser ? 'white' : '#333'};
            font-size: 14px;
            line-height: 1.4;
            border: ${isUser ? 'none' : '1px solid #e1e5e9'};
            ${isUser ? 'border-bottom-right-radius: 6px;' : 'border-bottom-left-radius: 6px;'}
            box-shadow: ${isUser ? '0 2px 8px rgba(102, 126, 234, 0.3)' : '0 2px 8px rgba(0,0,0,0.08)'};
        `;
        bubbleDiv.textContent = message;

        messageDiv.appendChild(bubbleDiv);
        chatMessages.appendChild(messageDiv);

        // Add bubbles
        if (bubbles && !isUser) {
            const bubblesContainer = document.createElement('div');
            bubblesContainer.style.cssText = `
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
                margin-top: 12px;
                justify-content: flex-start;
            `;

            bubbles.forEach(bubble => {
                const bubbleBtn = document.createElement('button');
                bubbleBtn.textContent = bubble.title;
                bubbleBtn.style.cssText = `
                    background: white;
                    border: 2px solid #667eea;
                    border-radius: 20px;
                    padding: 8px 16px;
                    font-size: 12px;
                    cursor: pointer;
                    color: #667eea;
                    font-weight: 500;
                `;
                bubbleBtn.addEventListener('click', () => sendBubble(bubble.payload));
                bubblesContainer.appendChild(bubbleBtn);
            });

            const bubblesWrapper = document.createElement('div');
            bubblesWrapper.style.cssText = 'display: flex; justify-content: flex-start; width: 100%;';
            bubblesWrapper.appendChild(bubblesContainer);
            chatMessages.appendChild(bubblesWrapper);
        }

        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function sendBubble(payload) {
        addMessage(payload, true);
        sendToBot(payload);
    }

    function sendMessage() {
        const input = document.getElementById('shipliyo-message-input');
        const message = input.value.trim();
        
        if (message) {
            addMessage(message, true);
            sendToBot(message);
            input.value = '';
        }
    }

    function sendToBot(message) {
        const chatMessages = document.getElementById('shipliyo-chat-messages');
        
        // Loading indicator
        const loadingDiv = document.createElement('div');
        loadingDiv.style.cssText = 'display: flex; justify-content: flex-start;';
        loadingDiv.innerHTML = `
            <div style="
                background: white;
                padding: 12px 16px;
                border-radius: 18px;
                border-bottom-left-radius: 6px;
                border: 1px solid #e1e5e9;
                font-size: 14px;
                color: #666;
            ">
                <div style="display: flex; gap: 4px;">
                    <div style="width: 6px; height: 6px; background: #667eea; border-radius: 50%;"></div>
                    <div style="width: 6px; height: 6px; background: #667eea; border-radius: 50%;"></div>
                    <div style="width: 6px; height: 6px; background: #667eea; border-radius: 50%;"></div>
                </div>
            </div>
        `;
        chatMessages.appendChild(loadingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        // API Call - PRODUCTION URL
        fetch(config.apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                language: config.language,
                session_id: sessionId
            })
        })
        .then(response => response.json())
        .then(data => {
            chatMessages.removeChild(loadingDiv);
            
            if (data.success) {
                addMessage(data.response, false, data.bubbles);
            } else {
                addMessage('❌ ' + data.response, false);
            }
        })
        .catch(error => {
            chatMessages.removeChild(loadingDiv);
            addMessage('❌ Bağlantı hatası. Lütfen tekrar deneyin.', false);
        });
    }

    // Initialize
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', createWidget);
    } else {
        createWidget();
    }

})();