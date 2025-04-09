// Get CSRF token
const DEBUG = true;


function log(...args) {
    if (DEBUG) {
        console.log(...args);
    }
}
function getCSRFToken() {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') return value;
    }
    return null;
}

function handleFetchError(error) {
    console.error('Error:', error);
    if (error.message === 'Failed to fetch') {
        addMessage('bot', 'Sorry, I cannot connect to the server right now. Please try again later.');
    } else {
        addMessage('bot', 'Sorry, I encountered an error. Please try again.');
    }
}

let chatVisible = false;

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initChatWidget();
});

function initChatWidget() {
    const input = document.getElementById('botMessageInput');
    if (input) {
        input.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendBotMessage();
            }
        });
    }
}

function initChatContent() {
    const chatContainer = document.getElementById('chatContainer');
    if (!chatContainer.querySelector('.chat-messages')) {
        const messagesDiv = document.getElementById('botMessages');
        if (messagesDiv) {
            messagesDiv.innerHTML = `
                <div class="message bot">
                    <div class="message-content">
                        <p>Hi 👋 How can I help you?</p>
                        <div class="quick-replies">
                            <button onclick="sendQuickReply('Track my order')">Track my order 📦</button>
                            <button onclick="sendQuickReply('How do I track my order?')">How do I track my order (FAQ)?</button>
                            <button onclick="sendQuickReply('Contact seller')">Contact seller</button>
                            <button onclick="sendQuickReply('Product information')">Product information</button>
                        </div>
                    </div>
                </div>
            `;
        }
    }
}

function toggleChat() {
    const chatContainer = document.getElementById('chatContainer');
    chatContainer.style.display = chatContainer.style.display === 'none' ? 'flex' : 'none';
}

async function sendBotMessage() {
    const messageInput = document.getElementById('botMessageInput');
    const message = messageInput.value.trim();
    
    if (message) {
        try {
            // Add user message to chat
            addMessageToChat('user', message);
            messageInput.value = '';
            
            // Show typing indicator
            showTypingIndicator();

            const response = await fetch(CHATBOT_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ message: message })
            });

            // Hide typing indicator
            hideTypingIndicator();

            const data = await response.json();
            console.log('Chatbot response:', data); // For debugging

            if (data.status === 'success' && data.response) {
                addMessageToChat('bot', data.response);
            } else {
                throw new Error(data.message || 'Unknown error occurred');
            }
        } catch (error) {
            console.error('Error:', error);
            hideTypingIndicator();
            addMessageToChat('bot', 'Sorry, I encountered an error. Please try again.');
        }
    }
}

function showTypingIndicator() {
    const chatMessages = document.getElementById('botMessages');
    const typingIndicator = document.createElement('div');
    typingIndicator.id = 'typingIndicator';
    typingIndicator.className = 'message bot typing';
    typingIndicator.innerHTML = `
        <div class="message-content">
            <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    `;
    chatMessages.appendChild(typingIndicator);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function hideTypingIndicator() {
    const typingIndicator = document.getElementById('typingIndicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

function addMessageToChat(sender, message) {
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
    
    // Add timestamp
    const timestamp = document.createElement('div');
    timestamp.className = 'message-timestamp';
    timestamp.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    messageContent.appendChild(timestamp);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function sendQuickReply(message) {
    const messageInput = document.getElementById('botMessageInput');
    messageInput.value = message;
    sendBotMessage();
}

function getCookie(name) {
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

// Add event listener for Enter key
document.addEventListener('DOMContentLoaded', function() {
    const messageInput = document.getElementById('botMessageInput');
    messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendBotMessage();
        }
    });
});