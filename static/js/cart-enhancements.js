// Additional cart enhancement functions for auto-update

/**
 * Update cart item with AJAX
 * @param {number} itemId - Cart item ID
 * @param {number} quantity - New quantity
 */
async function updateCartItem(itemId, quantity) {
    if (!itemId) return;

    const button = event.target;
    const originalText = button.innerHTML;
    button.disabled = true;
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';

    try {
        const formData = new FormData();
        formData.append('quantity', quantity);
        formData.append('csrfmiddlewaretoken', getCookie('csrftoken'));

        const response = await fetch(`/cart/update/${itemId}/`, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            },
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            // Update cart count in nav
            updateCartCountFromServer(data.cart_count);
            showNotification('تم تحديث السلة بنجاح', 'success');

            // Refresh page to show updated totals
            location.reload();
        } else {
            showNotification(data.message || 'حدث خطأ', 'error');
        }
    } catch (error) {
        console.error('Error updating cart:', error);
        showNotification('حدث خطأ أثناء تحديث السلة', 'error');
    } finally {
        button.disabled = false;
        button.innerHTML = originalText;
    }
}

/**
 * Remove item from cart with confirmation
 * @param {number} itemId - Cart item ID
 */
async function removeCartItem(itemId) {
    // Show custom confirmation modal
    showConfirmModal(
        'سيتم حذف هذا المنتج من سلة التسوق نهائياً',
        'تأكيد الحذف',
        async function () {
            const button = event.target;
            const originalText = button.innerHTML;
            button.disabled = true;
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';

            try {
                const formData = new FormData();
                formData.append('csrfmiddlewaretoken', getCookie('csrftoken'));

                const response = await fetch(`/cart/remove/${itemId}/`, {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                    body: formData
                });

                const data = await response.json();

                if (data.success) {
                    updateCartCountFromServer(data.cart_count);
                    showNotification('تم حذف المنتج من السلة', 'success');

                    // Remove item row from DOM
                    const itemRow = button.closest('.cart-item, tr');
                    if (itemRow) {
                        itemRow.style.animation = 'fadeOut 0.3s ease';
                        setTimeout(() => {
                            itemRow.remove();
                            // Reload if cart is now empty
                            if (data.cart_count === 0) {
                                location.reload();
                            }
                        }, 300);
                    }
                } else {
                    showNotification('⚠️ عذراً! لم نتمكن من حذف المنتج. يرجى المحاولة مرة أخرى', 'error');
                }
            } catch (error) {
                console.error('Error removing item:', error);
                showNotification('⚠️ حدث خطأ غير متوقع! يرجى تحديث الصفحة والمحاولة مرة أخرى', 'error');
            } finally {
                button.disabled = false;
                button.innerHTML = originalText;
            }
        }
    );
}

/**
 * Update cart count display from server response
 * @param {number} count - New cart count
 */
function updateCartCountFromServer(count) {
    const cartCountElements = document.querySelectorAll('#cart-count, .cart-count');
    cartCountElements.forEach(element => {
        element.textContent = count;

        // Add bounce animation
        element.style.animation = 'bounce 0.5s ease';
        setTimeout(() => {
            element.style.animation = '';
        }, 500);
    });
}

/**
 * Increment quantity input
 * @param {HTMLElement} input - Quantity input element
 */
function incrementQuantity(input) {
    const currentValue = parseInt(input.value) || 1;
    const maxValue = parseInt(input.max) || 100;
    if (currentValue < maxValue) {
        input.value = currentValue + 1;
        input.dispatchEvent(new Event('change'));
    }
}

/**
 * Decrement quantity input
 * @param {HTMLElement} input - Quantity input element
 */
function decrementQuantity(input) {
    const currentValue = parseInt(input.value) || 1;
    const minValue = parseInt(input.min) || 1;
    if (currentValue > minValue) {
        input.value = currentValue - 1;
        input.dispatchEvent(new Event('change'));
    }
}

// Auto-update cart when quantity changes
document.addEventListener('DOMContentLoaded', function () {
    // Attach event listeners to quantity inputs
    const quantityInputs = document.querySelectorAll('.quantity-input');
    quantityInputs.forEach(input => {
        let timeoutId;
        input.addEventListener('change', function () {
            clearTimeout(timeoutId);
            const itemId = this.dataset.itemId;
            const quantity = parseInt(this.value);

            if (itemId && quantity > 0) {
                // Debounce the update
                timeoutId = setTimeout(() => {
                    updateCartItem(itemId, quantity);
                }, 500);
            }
        });
    });
});

// CSS Animations (add to your stylesheet)
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeOut {
        from { opacity: 1; transform: translateX(0); }
        to { opacity: 0; transform: translateX(-20px); }
    }
    
    @keyframes bounce {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.2); }
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes slideOut {
        from { opacity: 1; transform: translateY(0); }
        to { opacity: 0; transform: translateY(-20px); }
    }
`;
document.head.appendChild(style);
