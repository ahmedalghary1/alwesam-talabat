// ==================== CUSTOMER SUPPORT CHAT SYSTEM ====================

const SUPPORT_REFRESH_INTERVAL_MS = 1500;
let supportRefreshTimer = null;
let supportRefreshInFlight = false;

function initSupportChat() {
    const chatWindow = document.getElementById('supportChatWindow');
    const floatingBtn = document.getElementById('supportFloatingBtn');
    const messageInput = document.getElementById('supportMessageInput');
    const sendBtn = document.getElementById('supportSendBtn');
    const closeBtn = document.getElementById('supportCloseBtn');

    if (!chatWindow || !floatingBtn) return;

    floatingBtn.addEventListener('click', toggleSupportChat);

    if (closeBtn) {
        closeBtn.addEventListener('click', toggleSupportChat);
    }

    if (sendBtn) {
        sendBtn.addEventListener('click', sendSupportMessage);
    }

    if (messageInput) {
        messageInput.addEventListener('keydown', function (event) {
            if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault();
                sendSupportMessage();
            }
        });
    }
}

function toggleSupportChat() {
    const chatWindow = document.getElementById('supportChatWindow');
    if (!chatWindow) return;

    if (chatWindow.classList.contains('active')) {
        chatWindow.classList.remove('active');
        stopSupportRefresh();
        return;
    }

    chatWindow.classList.add('active');
    loadUserMessages();
    startSupportRefresh();
}

function sendSupportMessage() {
    const messageInput = document.getElementById('supportMessageInput');
    const sendBtn = document.getElementById('supportSendBtn');
    if (!messageInput) return;

    const messageText = messageInput.value.trim();
    if (!messageText) return;

    const pendingMessage = displayMessage({
        text: messageText,
        created_at: new Date().toLocaleString('ar-EG'),
        is_user: true,
        pending: true
    });

    messageInput.value = '';
    if (sendBtn) sendBtn.disabled = true;

    fetch('/support/send/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken(),
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({ message: messageText })
    })
        .then(async response => {
            const data = await response.json();
            if (!response.ok || !data.success) {
                throw new Error(data.error || 'حدث خطأ في إرسال الرسالة');
            }
            return data;
        })
        .then(data => {
            const savedMessage = findRenderedMessage('message', data.message.id);

            // A refresh can render the stored message before the send request resolves.
            if (savedMessage && savedMessage !== pendingMessage) {
                pendingMessage.remove();
            } else {
                pendingMessage.dataset.supportMessageId = String(data.message.id);
                pendingMessage.classList.remove('pending');
                const time = pendingMessage.querySelector('.support-message-time');
                if (time) time.textContent = data.message.created_at;
            }

            refreshSupportMessages();
        })
        .catch(error => {
            console.error('Support message error:', error);
            pendingMessage.classList.add('failed');
            showErrorMessage(error.message || 'حدث خطأ في الاتصال بالخادم');
        })
        .finally(() => {
            if (sendBtn) sendBtn.disabled = false;
            messageInput.focus();
        });
}

function loadUserMessages() {
    showDefaultWelcomeMessage();
    return refreshSupportMessages();
}

// Synchronize messages while the floating chat is open, without a page reload.
function refreshSupportMessages() {
    if (supportRefreshInFlight) return Promise.resolve();
    supportRefreshInFlight = true;

    return fetch('/support/messages/', {
        method: 'GET',
        cache: 'no-store',
        headers: {
            'X-CSRFToken': getCsrfToken(),
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
        .then(async response => {
            const data = await response.json();
            if (!response.ok || !data.success) {
                throw new Error(data.error || 'تعذر تحميل المحادثة');
            }
            return data;
        })
        .then(data => {
            data.messages.forEach(message => {
                displayMessage({
                    id: message.id,
                    record_type: 'message',
                    text: message.text,
                    created_at: message.created_at,
                    is_user: !message.is_admin,
                    admin_name: message.admin
                });

                (message.replies || []).forEach(reply => {
                    displayMessage({
                        id: reply.id,
                        text: reply.text,
                        created_at: reply.created_at,
                        is_user: false,
                        admin_name: reply.admin
                    });
                });
            });
        })
        .catch(error => {
            console.error('Support refresh error:', error);
        })
        .finally(() => {
            supportRefreshInFlight = false;
        });
}

function startSupportRefresh() {
    stopSupportRefresh();
    supportRefreshTimer = window.setInterval(() => {
        const chatWindow = document.getElementById('supportChatWindow');
        if (chatWindow && chatWindow.classList.contains('active') && !document.hidden) {
            refreshSupportMessages();
        }
    }, SUPPORT_REFRESH_INTERVAL_MS);
}

function stopSupportRefresh() {
    if (supportRefreshTimer !== null) {
        window.clearInterval(supportRefreshTimer);
        supportRefreshTimer = null;
    }
}

function findRenderedMessage(type, id) {
    if (id === undefined || id === null) return null;

    const attribute = type === 'reply' ? 'supportReplyId' : 'supportMessageId';
    return Array.from(document.querySelectorAll('#supportChatBody .support-message')).find(
        element => element.dataset[attribute] === String(id)
    ) || null;
}

function displayMessage(messageData) {
    const chatBody = document.getElementById('supportChatBody');
    if (!chatBody) return null;

    const messageType = messageData.record_type || (messageData.is_user ? 'message' : 'reply');
    const existingMessage = findRenderedMessage(messageType, messageData.id);
    if (existingMessage) return existingMessage;

    const messageDiv = document.createElement('div');
    messageDiv.className = messageData.is_user ? 'support-message user' : 'support-message admin';
    if (messageData.pending) messageDiv.classList.add('pending');

    if (messageData.id !== undefined && messageData.id !== null) {
        const attribute = messageType === 'message' ? 'supportMessageId' : 'supportReplyId';
        messageDiv.dataset[attribute] = String(messageData.id);
    }

    let content = '';
    if (!messageData.is_user) {
        const adminName = messageData.admin_name || 'خدمة العملاء';
        content += `
            <div class="support-admin-label">
                <i class="fas fa-headset"></i>
                ${escapeHtml(adminName)}
            </div>
        `;
    }

    content += `
        <div class="support-message-content">
            ${escapeHtml(messageData.text)}
            <span class="support-message-time">${escapeHtml(messageData.created_at)}</span>
        </div>
    `;

    messageDiv.innerHTML = content;
    chatBody.appendChild(messageDiv);
    autoScrollToBottom();
    return messageDiv;
}

function showDefaultWelcomeMessage() {
    const chatBody = document.getElementById('supportChatBody');
    if (!chatBody || chatBody.querySelector('.support-message.welcome')) return;

    const welcomeDiv = document.createElement('div');
    welcomeDiv.className = 'support-message welcome';
    welcomeDiv.innerHTML = `
        <div class="support-message-content">
            <strong>مرحباً بك في خدمة العملاء!</strong>
            نحن هنا لمساعدتك. اكتب رسالتك وسنرد عليك في أقرب وقت ممكن.
        </div>
    `;
    chatBody.appendChild(welcomeDiv);
}

function showErrorMessage(errorText) {
    const chatBody = document.getElementById('supportChatBody');
    if (!chatBody) return;

    const errorDiv = document.createElement('div');
    errorDiv.className = 'support-message admin';
    errorDiv.innerHTML = `
        <div class="support-message-content" style="border-color: #ef4444; background: rgba(239, 68, 68, 0.1); color: #ef4444;">
            <i class="fas fa-exclamation-circle"></i> ${escapeHtml(errorText)}
        </div>
    `;
    chatBody.appendChild(errorDiv);
    autoScrollToBottom();
}

function autoScrollToBottom() {
    const chatBody = document.getElementById('supportChatBody');
    if (chatBody) chatBody.scrollTop = chatBody.scrollHeight;
}

function getCsrfToken() {
    const csrfInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
    if (csrfInput) return csrfInput.value;

    const name = 'csrftoken';
    if (!document.cookie) return null;

    const cookie = document.cookie.split(';').map(item => item.trim()).find(
        item => item.substring(0, name.length + 1) === `${name}=`
    );
    return cookie ? decodeURIComponent(cookie.substring(name.length + 1)) : null;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text === undefined || text === null ? '' : String(text);
    return div.innerHTML;
}

document.addEventListener('DOMContentLoaded', initSupportChat);

document.addEventListener('visibilitychange', function () {
    const chatWindow = document.getElementById('supportChatWindow');
    if (!chatWindow || !chatWindow.classList.contains('active')) return;

    if (document.hidden) {
        stopSupportRefresh();
    } else {
        refreshSupportMessages();
        startSupportRefresh();
    }
});
