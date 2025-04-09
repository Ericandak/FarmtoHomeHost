// static/Products/js/chat-init.js
class ChatWidget {
    constructor() {
        this.initialize();
    }

    initialize() {
        this.addMessageToChat('bot', 'Hello! 👋 How can I help you today? You can ask me about:\n' +
            '• Product information\n' +
            '• Order tracking\n' +
            '• Farming questions\n' +
            '• General assistance');
    }

    async sendBotMessage() {
        const messageInput = document.getElementById('botMessageInput');
        const message = messageInput.value.trim();
        
        if (message) {
            try {
                this.addMessageToChat('user', message);
                messageInput.value = '';
                this.showTypingIndicator();

                const response = await fetch(CHATBOT_URL, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCookie('csrftoken')
                    },
                    body: JSON.stringify({ message: message })
                });

                this.hideTypingIndicator();
                const data = await response.json();

                if (data.status === 'success' && data.response) {
                    this.addMessageToChat('bot', data.response);
                } else {
                    throw new Error(data.message || 'Unknown error occurred');
                }
            } catch (error) {
                console.error('Error:', error);
                this.hideTypingIndicator();
                this.addMessageToChat('bot', 'Sorry, I encountered an error. Please try again.');
            }
        }
    }

    addMessageToChat(sender, message) {
        const chatMessages = document.getElementById('botMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        const messageText = document.createElement('p');
        messageText.innerHTML = message.split('\n').join('<br>');
        
        messageContent.appendChild(messageText);
        messageDiv.appendChild(messageContent);
        chatMessages.appendChild(messageDiv);
        
        const timestamp = document.createElement('div');
        timestamp.className = 'message-timestamp';
        timestamp.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        messageContent.appendChild(timestamp);
        
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    showTypingIndicator() {
        const chatMessages = document.getElementById('botMessages');
        const typingIndicator = document.createElement('div');
        typingIndicator.id = 'typingIndicator';
        typingIndicator.className = 'message bot typing';
        typingIndicator.innerHTML = `
            <div class="message-content">
                <div class="typing-indicator">
                    <span></span><span></span><span></span>
                </div>
            </div>
        `;
        chatMessages.appendChild(typingIndicator);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    toggleChat() {
        const chatContainer = document.getElementById('chatContainer');
        chatContainer.style.display = chatContainer.style.display === 'none' ? 'flex' : 'none';
    }

    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
}

// Initialize chat widget
let chatWidget;
document.addEventListener('DOMContentLoaded', () => {
    chatWidget = new ChatWidget();
    
    // Make functions globally available
    window.toggleChat = () => chatWidget.toggleChat();
    window.sendBotMessage = () => chatWidget.sendBotMessage();
    
    // Add enter key listener
    const messageInput = document.getElementById('botMessageInput');
    if (messageInput) {
        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                chatWidget.sendBotMessage();
            }
        });
    }
});