// ==================== CUSTOMER SUPPORT CHAT SYSTEM ====================

// Initialize support chat system
function initSupportChat() {
    const chatWindow = document.getElementById('supportChatWindow');
    const floatingBtn = document.getElementById('supportFloatingBtn');
    const chatBody = document.getElementById('supportChatBody');
    const messageInput = document.getElementById('supportMessageInput');
    const sendBtn = document.getElementById('supportSendBtn');
    const closeBtn = document.getElementById('supportCloseBtn');

    if (!chatWindow || !floatingBtn) return;

    // Load messages when window is first opened
    let messagesLoaded = false;

    // Toggle chat window open/close
    floatingBtn.addEventListener('click', function () {
        toggleSupportChat();
    });

    if (closeBtn) {
        closeBtn.addEventListener('click', function () {
            toggleSupportChat();
        });
    }

    // Send message button handler
    if (sendBtn) {
        sendBtn.addEventListener('click', function () {
            sendSupportMessage();
        });
    }

    // Send on Enter key (Shift+Enter for new line)
    if (messageInput) {
        messageInput.addEventListener('keypress', function (e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendSupportMessage();
            }
        });
    }
}

// Toggle support chat window
function toggleSupportChat() {
    const chatWindow = document.getElementById('supportChatWindow');
    const isActive = chatWindow.classList.contains('active');

    if (isActive) {
        chatWindow.classList.remove('active');
    } else {
        chatWindow.classList.add('active');
        // Load messages on first open
        if (!window.supportMessagesLoaded) {
            loadUserMessages();
            window.supportMessagesLoaded = true;
        }
    }
}

// Send new support message
function sendSupportMessage() {
    const messageInput = document.getElementById('supportMessageInput');
    const messageText = messageInput.value.trim();

    if (!messageText) return;

    // Display message immediately in interface
    displayMessage({
        text: messageText,
        created_at: new Date().toLocaleString('ar-EG'),
        is_user: true
    });

    // Clear input field
    messageInput.value = '';

    // Send message to server
    fetch('/support/send/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({
            message: messageText
        })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log('تم إرسال الرسالة بنجاح');
            } else {
                console.error('خطأ:', data.error);
                showErrorMessage('حدث خطأ في إرسال الرسالة');
            }
        })
        .catch(error => {
            console.error('خطأ:', error);
            showErrorMessage('حدث خطأ في الاتصال بالخادم');
        });
}

// Load user messages from server
function loadUserMessages() {
    const chatBody = document.getElementById('supportChatBody');

    // Show welcome message first
    showDefaultWelcomeMessage();

    // Fetch messages from server
    fetch('/support/messages/', {
        method: 'GET',
        headers: {
            'X-CSRFToken': getCsrfToken()
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.success && data.messages) {
                // Display messages and replies
                data.messages.forEach(msg => {
                    displayMessage({
                        text: msg.text,
                        created_at: msg.created_at,
                        is_user: true
                    });

                    // Display replies
                    if (msg.replies && msg.replies.length > 0) {
                        msg.replies.forEach(reply => {
                            displayMessage({
                                text: reply.text,
                                created_at: reply.created_at,
                                is_user: false,
                                admin_name: reply.admin
                            });
                        });
                    }
                });

                autoScrollToBottom();
            }
        })
        .catch(error => {
            console.error('خطأ في تحميل الرسائل:', error);
        });
}

// Display message in chat window
function displayMessage(messageData) {
    const chatBody = document.getElementById('supportChatBody');
    const messageDiv = document.createElement('div');
    messageDiv.className = messageData.is_user ? 'support-message user' : 'support-message admin';

    let content = '';

    if (!messageData.is_user) {
        // Add admin label with icon
        const adminName = messageData.admin_name || 'خدمة العملاء';
        content += `
            <div class="support-admin-label">
                <i class="fas fa-headset"></i>
                خدمة العملاء
            </div>
        `;
    }

    content += `
        <div class="support-message-content">
            ${escapeHtml(messageData.text)}
            <span class="support-message-time">${messageData.created_at}</span>
        </div>
    `;

    messageDiv.innerHTML = content;
    chatBody.appendChild(messageDiv);
    autoScrollToBottom();
}

// Show default welcome message
function showDefaultWelcomeMessage() {
    const chatBody = document.getElementById('supportChatBody');

    // Check if welcome message already exists
    if (chatBody.querySelector('.support-message.welcome')) {
        return;
    }

    const welcomeDiv = document.createElement('div');
    welcomeDiv.className = 'support-message welcome';
    welcomeDiv.innerHTML = `
        <div class="support-message-content">
            <strong>مرحباً بك في خدمة العملاء! 👋</strong>
            نحن هنا لمساعدتك. اكتب رسالتك وسنرد عليك في أقرب وقت ممكن.
        </div>
    `;

    chatBody.appendChild(welcomeDiv);
}

// Show error message
function showErrorMessage(errorText) {
    const chatBody = document.getElementById('supportChatBody');
    const errorDiv = document.createElement('div');
    errorDiv.className = 'support-message admin';
    errorDiv.innerHTML = `
        <div class="support-message-content" style="border-color: #ef4444; background: rgba(239, 68, 68, 0.1); color: #ef4444;">
            <i class="fas fa-exclamation-circle"></i> ${errorText}
        </div>
    `;
    chatBody.appendChild(errorDiv);
    autoScrollToBottom();
}

// Auto-scroll to bottom of chat window
function autoScrollToBottom() {
    const chatBody = document.getElementById('supportChatBody');
    if (chatBody) {
        chatBody.scrollTop = chatBody.scrollHeight;
    }
}

// Get CSRF token for API requests
function getCsrfToken() {
    const csrfInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
    if (csrfInput) {
        return csrfInput.value;
    }

    // Try to get from cookies as fallback
    const name = 'csrftoken';
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

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function () {
    initSupportChat();
});
