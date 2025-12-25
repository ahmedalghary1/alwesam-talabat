// ==================== الوسام طلبات - Cart System ====================
// Professional Cart Management with localStorage + Server sync

// ==================== UTILITY FUNCTIONS ====================
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

// ==================== THEME TOGGLE ====================
function toggleTheme() {
    const body = document.body;
    const currentTheme = body.classList.contains('theme-dark') ? 'theme-dark' : 'theme-light';
    const newTheme = currentTheme === 'theme-dark' ? 'theme-light' : 'theme-dark';

    body.classList.remove(currentTheme);
    body.classList.add(newTheme);

    const themeIcon = document.getElementById('theme-icon');
    if (themeIcon) {
        themeIcon.className = newTheme === 'theme-dark' ? 'fas fa-sun' : 'fas fa-moon';
    }

    fetch('/accounts/set-theme/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({ theme: newTheme })
    }).catch(error => console.error('Error saving theme:', error));
}

// ==================== LANGUAGE TOGGLE ====================
function toggleLanguage() {
    const html = document.documentElement;
    const currentLang = html.getAttribute('lang') || 'ar';
    const newLang = currentLang === 'ar' ? 'en' : 'ar';
    const newDir = newLang === 'ar' ? 'rtl' : 'ltr';

    html.setAttribute('lang', newLang);
    html.setAttribute('dir', newDir);

    fetch('/accounts/set-language/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({ language: newLang })
    }).then(() => location.reload())
        .catch(error => console.error('Error saving language:', error));
}

// ==================== MOBILE MENU ====================
function toggleMenu() {
    const navMenu = document.getElementById('nav-menu');
    if (navMenu) {
        navMenu.classList.toggle('active');
    }
}

// ==================== CART MANAGEMENT - LOCALSTORAGE ====================
const CartManager = {
    STORAGE_KEY: 'alwesam_cart',

    // Get cart from localStorage
    getCart() {
        try {
            const cart = localStorage.getItem(this.STORAGE_KEY);
            return cart ? JSON.parse(cart) : [];
        } catch (e) {
            console.error('Error reading cart:', e);
            return [];
        }
    },

    // Save cart to localStorage
    saveCart(cart) {
        try {
            localStorage.setItem(this.STORAGE_KEY, JSON.stringify(cart));
            this.updateBadge();
        } catch (e) {
            console.error('Error saving cart:', e);
        }
    },

    // Add item to cart
    addItem(productId, productName, quantity, pcsCarton, imageUrl, variantId = null, unitType = 'carton', sizeName = '') {
        let cart = this.getCart();

        // Convert to pieces if ordering by carton
        let quantityInPieces = quantity;
        if (unitType === 'carton') {
            quantityInPieces = quantity * (pcsCarton || 1);
        }

        // Find existing item (match by product_id, variant_id, unit_type, and size_name)
        const existingIndex = cart.findIndex(item =>
            item.product_id === productId &&
            item.variant_id === variantId &&
            item.unit_type === unitType &&
            (item.size_name || '') === sizeName
        );

        if (existingIndex !== -1) {
            cart[existingIndex].quantity += quantityInPieces;
        } else {
            cart.push({
                product_id: productId,
                product_name: productName,
                quantity: quantityInPieces,  // Always store in pieces
                pcs_carton: pcsCarton,
                image_url: imageUrl,
                variant_id: variantId,
                unit_type: unitType,  // NEW
                size_name: sizeName,  // NEW: Store size name
                added_at: new Date().toISOString()
            });
        }

        this.saveCart(cart);
        return true;
    },

    // Update item quantity
    updateItem(productId, quantity, variantId = null, unitType = 'carton') {
        let cart = this.getCart();
        const index = cart.findIndex(item =>
            item.product_id === productId &&
            item.variant_id === variantId &&
            (item.unit_type || 'carton') === unitType
        );

        if (index !== -1) {
            if (quantity > 0) {
                cart[index].quantity = quantity;
            } else {
                cart.splice(index, 1);
            }
            this.saveCart(cart);
        }
    },

    // Remove item from cart
    removeItem(productId, variantId = null, unitType = 'carton') {
        let cart = this.getCart();
        cart = cart.filter(item =>
            !(item.product_id === productId &&
                item.variant_id === variantId &&
                (item.unit_type || 'carton') === unitType)
        );
        this.saveCart(cart);
    },

    // Clear entire cart
    clearCart() {
        localStorage.removeItem(this.STORAGE_KEY);
        this.updateBadge();
    },

    // Get total items count
    getTotalCount() {
        const cart = this.getCart();
        return cart.reduce((sum, item) => sum + item.quantity, 0);
    },

    // Update cart badge in navbar
    updateBadge() {
        const badges = document.querySelectorAll('#cart-count, .cart-badge');
        const count = this.getTotalCount();
        badges.forEach(badge => {
            if (badge) badge.textContent = count;
        });
    },

    // Check if cart has items
    hasItems() {
        return this.getCart().length > 0;
    },

    // Sync cart to server (for logged-in users)
    async syncToServer() {
        const cart = this.getCart();
        if (cart.length === 0) return { success: true, message: 'Cart is empty' };

        try {
            const response = await fetch('/cart/sync/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({ cart_items: cart })
            });

            const data = await response.json();

            if (data.success) {
                // Clear localStorage after successful sync
                this.clearCart();
                console.log('Cart synced successfully:', data.message);
            }

            return data;
        } catch (error) {
            console.error('Error syncing cart:', error);
            return { success: false, message: error.message };
        }
    }
};

// ==================== GLOBAL CART FUNCTIONS ====================
// Legacy support - these call CartManager internally

function getCartFromLocal() {
    return CartManager.getCart();
}

function updateCartCount() {
    // Only update from localStorage if user is NOT authenticated
    // For authenticated users, Django renders the correct count via context processor
    const isAuthenticated = document.body.dataset.userAuthenticated === 'true';
    if (!isAuthenticated) {
        CartManager.updateBadge();
    }
}

function addToCartLocal(productId, productName, quantity, pcsCarton, imageUrl, variantId = null) {
    CartManager.addItem(productId, productName, quantity, pcsCarton, imageUrl, variantId);
}

function updateCartLocal(productId, quantity, variantId = null, unitType = 'carton') {
    CartManager.updateItem(productId, quantity, variantId, unitType);
}

function removeFromCartLocal(productId, variantId = null, unitType = 'carton') {
    CartManager.removeItem(productId, variantId, unitType);
}

// ==================== ADD TO CART - UNIVERSAL FUNCTION ====================
async function addToCart(productId, productName, quantity, pcsCarton, imageUrl, isAuthenticated, variantId = null, unitType = 'carton', sizeName = '') {
    if (isAuthenticated) {
        // Authenticated user - add via server
        try {
            // Get CSRF token - try hidden input first, then cookie
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || getCookie('csrftoken');

            if (!csrfToken) {
                console.error('CSRF token not found');
                showNotification('خطأ في الأمان - يرجى إعادة تحميل الصفحة', 'error');
                return { success: false, error: 'CSRF token missing' };
            }

            const formData = new FormData();
            formData.append('quantity', quantity);
            formData.append('unit_type', unitType);  // NEW
            formData.append('csrfmiddlewaretoken', csrfToken);
            if (variantId) {
                formData.append('variant_id', variantId);
            }
            if (sizeName) {
                formData.append('size_name', sizeName);  // NEW: Add size_name
            }

            const response = await fetch(`/cart/add/${productId}/`, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrfToken
                },
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                // Update badge from server response
                const badges = document.querySelectorAll('#cart-count, .cart-badge');
                badges.forEach(badge => {
                    if (badge && data.cart_count !== undefined) {
                        badge.textContent = data.cart_count;
                    }
                });
                showNotification(data.message, 'success');
                return { success: true, data };
            } else {
                showNotification(data.message || 'حدث خطأ أثناء إضافة المنتج', 'error');
                return { success: false, data };
            }
        } catch (error) {
            console.error('Error adding to cart:', error);
            showNotification('حدث خطأ في الاتصال', 'error');
            return { success: false, error };
        }
    } else {
        // Non-authenticated user - use localStorage
        CartManager.addItem(productId, productName, quantity, pcsCarton, imageUrl, variantId, unitType, sizeName);
        showNotification(`تم إضافة ${productName} إلى السلة`, 'success');
        return { success: true };
    }
}

// ==================== NOTIFICATION SYSTEM ====================
function showNotification(message, type = 'info') {
    // Remove any existing notification
    const existing = document.querySelector('.global-notification');
    if (existing) existing.remove();

    const notification = document.createElement('div');
    notification.className = `global-notification notification-${type}`;

    const icon = type === 'success' ? 'fa-check-circle' :
        type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle';
    const bgColor = type === 'success' ? 'linear-gradient(135deg, #22c55e, #16a34a)' :
        type === 'error' ? 'linear-gradient(135deg, #ef4444, #dc2626)' :
            'linear-gradient(135deg, #3b82f6, #2563eb)';

    notification.innerHTML = `<i class="fas ${icon}"></i> <span>${message}</span>`;
    notification.style.cssText = `
        position: fixed;
        bottom: 2rem;
        left: 50%;
        transform: translateX(-50%) translateY(100px);
        padding: 1rem 2rem;
        background: ${bgColor};
        color: #fff;
        border-radius: 14px;
        z-index: 99999;
        box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        opacity: 0;
        transition: all 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
    `;

    document.body.appendChild(notification);

    // Animate in
    requestAnimationFrame(() => {
        notification.style.transform = 'translateX(-50%) translateY(0)';
        notification.style.opacity = '1';
    });

    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.transform = 'translateX(-50%) translateY(100px)';
        notification.style.opacity = '0';
        setTimeout(() => notification.remove(), 400);
    }, 3000);
}

// ==================== AUTO SYNC ON PAGE LOAD ====================
document.addEventListener('DOMContentLoaded', function () {
    // Initialize theme icon
    const themeIcon = document.getElementById('theme-icon');
    const isDark = document.body.classList.contains('theme-dark');
    if (themeIcon) {
        themeIcon.className = isDark ? 'fas fa-sun' : 'fas fa-moon';
    }

    // Check if user is authenticated
    const isAuthenticated = document.body.dataset.userAuthenticated === 'true';

    // CRITICAL FIX: Only update badge from localStorage for non-authenticated users
    // For authenticated users, Django renders the count via context processor
    if (!isAuthenticated) {
        CartManager.updateBadge();
    }

    // Check if user just logged in and has items in localStorage
    if (isAuthenticated && CartManager.hasItems()) {
        // Auto-sync cart to server
        CartManager.syncToServer().then(result => {
            if (result.success && result.cart_count !== undefined) {
                const badges = document.querySelectorAll('#cart-count, .cart-badge');
                badges.forEach(badge => {
                    if (badge) badge.textContent = result.cart_count;
                });
            }
        });
    }
});

// Export for global access
window.CartManager = CartManager;
window.addToCart = addToCart;
window.addToCartLocal = addToCartLocal;
window.updateCartLocal = updateCartLocal;
window.removeFromCartLocal = removeFromCartLocal;
window.getCartFromLocal = getCartFromLocal;
window.updateCartCount = updateCartCount;
window.showNotification = showNotification;
window.getCookie = getCookie;
