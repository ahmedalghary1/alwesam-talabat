// ==================== CUSTOMER SUPPORT CHAT SYSTEM ====================

// تهيئة نظام الدردشة
function initSupportChat() {
    const chatWindow = document.getElementById('supportChatWindow');
    const floatingBtn = document.getElementById('supportFloatingBtn');
    const chatBody = document.getElementById('supportChatBody');
    const messageInput = document.getElementById('supportMessageInput');
    const sendBtn = document.getElementById('supportSendBtn');
    const closeBtn = document.getElementById('supportCloseBtn');

    if (!chatWindow || !floatingBtn) return;

    // تحميل الرسائل عند فتح النافذة لأول مرة
    let messagesLoaded = false;

    // فتح/إغلاق نافذة الدردشة
    floatingBtn.addEventListener('click', function () {
        toggleSupportChat();
    });

    if (closeBtn) {
        closeBtn.addEventListener('click', function () {
            toggleSupportChat();
        });
    }

    // إرسال الرسالة
    if (sendBtn) {
        sendBtn.addEventListener('click', function () {
            sendSupportMessage();
        });
    }

    // إرسال عند الضغط على Enter (مع Shift+Enter للسطر الجديد)
    if (messageInput) {
        messageInput.addEventListener('keypress', function (e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendSupportMessage();
            }
        });
    }
}

// فتح/إغلاق نافذة الدردشة
function toggleSupportChat() {
    const chatWindow = document.getElementById('supportChatWindow');
    const isActive = chatWindow.classList.contains('active');

    if (isActive) {
        chatWindow.classList.remove('active');
    } else {
        chatWindow.classList.add('active');
        // تحميل الرسائل عند الفتح لأول مرة
        if (!window.supportMessagesLoaded) {
            loadUserMessages();
            window.supportMessagesLoaded = true;
        }
    }
}

// إرسال رسالة جديدة
function sendSupportMessage() {
    const messageInput = document.getElementById('supportMessageInput');
    const messageText = messageInput.value.trim();

    if (!messageText) return;

    // إظهار الرسالة مباشرة في الواجهة
    displayMessage({
        text: messageText,
        created_at: new Date().toLocaleString('ar-EG'),
        is_user: true
    });

    // مسح حقل الإدخال
    messageInput.value = '';

    // إرسال الرسالة للسيرفر
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

// تحميل رسائل المستخدم
function loadUserMessages() {
    const chatBody = document.getElementById('supportChatBody');

    // إظهار الرسالة الترحيبية أولاً
    showDefaultWelcomeMessage();

    // تحميل الرسائل من السيرفر
    fetch('/support/messages/', {
        method: 'GET',
        headers: {
            'X-CSRFToken': getCsrfToken()
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.success && data.messages) {
                // عرض الرسائل والردود
                data.messages.forEach(msg => {
                    displayMessage({
                        text: msg.text,
                        created_at: msg.created_at,
                        is_user: true
                    });

                    // عرض الردود
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

// عرض رسالة في النافذة
function displayMessage(messageData) {
    const chatBody = document.getElementById('supportChatBody');
    const messageDiv = document.createElement('div');
    messageDiv.className = messageData.is_user ? 'support-message user' : 'support-message admin';

    let content = '';

    if (!messageData.is_user) {
        // إضافة label للمسؤول مع الأيقونة
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

// عرض الرسالة الترحيبية الافتراضية
function showDefaultWelcomeMessage() {
    const chatBody = document.getElementById('supportChatBody');

    // التحقق من عدم وجود رسالة ترحيبية مسبقاً
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

// عرض رسالة خطأ
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

// التمرير التلقائي لأسفل النافذة
function autoScrollToBottom() {
    const chatBody = document.getElementById('supportChatBody');
    if (chatBody) {
        chatBody.scrollTop = chatBody.scrollHeight;
    }
}

// الحصول على CSRF Token
function getCsrfToken() {
    const csrfInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
    if (csrfInput) {
        return csrfInput.value;
    }

    // محاولة الحصول من الكوكيز
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

// تنظيف النص من HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// تهيئة عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', function () {
    initSupportChat();
});
