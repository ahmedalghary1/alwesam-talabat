/**
 * Frontend Validation Utilities
 * Provides validation functions for cart and product quantities
 */

// Constants (should match backend constants)
const MAX_QUANTITY_PER_ITEM = 1000;
const MIN_QUANTITY = 1;

/**
 * Validate quantity input
 * @param {number} quantity - The quantity to validate
 * @param {string} unitType - 'carton' or 'piece'
 * @returns {Object} - {isValid: boolean, error: string}
 */
function validateQuantity(quantity, unitType = 'carton') {
    // Check if quantity is a number
    if (isNaN(quantity) || quantity === null || quantity === undefined) {
        return {
            isValid: false,
            error: 'الرجاء إدخال كمية صحيحة'
        };
    }

    // Convert to number
    const qty = Number(quantity);

    // Check if it's an integer
    if (!Number.isInteger(qty)) {
        return {
            isValid: false,
            error: 'الكمية يجب أن تكون رقماً صحيحاً'
        };
    }

    // Check minimum
    if (qty < MIN_QUANTITY) {
        return {
            isValid: false,
            error: `الكمية يجب أن تكون ${MIN_QUANTITY} على الأقل`
        };
    }

    // Check maximum
    if (qty > MAX_QUANTITY_PER_ITEM) {
        return {
            isValid: false,
            error: `الكمية القصوى هي ${MAX_QUANTITY_PER_ITEM}`
        };
    }

    return {
        isValid: true,
        error: null
    };
}

/**
 * Show validation error message
 * @param {string} message - Error message to display
 * @param {HTMLElement} inputElement - The input element to highlight
 */
function showValidationError(message, inputElement) {
    // Create or update error message element
    let errorDiv = inputElement.parentElement.querySelector('.validation-error');

    if (!errorDiv) {
        errorDiv = document.createElement('div');
        errorDiv.className = 'validation-error';
        errorDiv.style.color = '#ef4444';
        errorDiv.style.fontSize = '0.875rem';
        errorDiv.style.marginTop = '0.25rem';
        inputElement.parentElement.appendChild(errorDiv);
    }

    errorDiv.textContent = message;

    // Highlight input
    inputElement.style.borderColor = '#ef4444';

    // Remove error after 3 seconds
    setTimeout(() => {
        if (errorDiv && errorDiv.parentElement) {
            errorDiv.remove();
        }
        inputElement.style.borderColor = '';
    }, 3000);
}

/**
 * Clear validation error
 * @param {HTMLElement} inputElement - The input element
 */
function clearValidationError(inputElement) {
    const errorDiv = inputElement.parentElement.querySelector('.validation-error');
    if (errorDiv) {
        errorDiv.remove();
    }
    inputElement.style.borderColor = '';
}

/**
 * Validate and sanitize quantity input in real-time
 * @param {HTMLInputElement} input - The input element
 */
function setupQuantityValidation(input) {
    if (!input) return;

    // Validate on input
    input.addEventListener('input', function (e) {
        const value = e.target.value;

        // Remove non-numeric characters
        const sanitized = value.replace(/[^0-9]/g, '');

        if (sanitized !== value) {
            e.target.value = sanitized;
        }

        // Clear previous errors
        clearValidationError(e.target);
    });

    // Validate on blur
    input.addEventListener('blur', function (e) {
        const value = e.target.value;

        if (value === '') {
            e.target.value = MIN_QUANTITY;
            return;
        }

        const validation = validateQuantity(value);

        if (!validation.isValid) {
            showValidationError(validation.error, e.target);
            e.target.value = MIN_QUANTITY;
        }
    });

    // Prevent negative values
    input.addEventListener('keydown', function (e) {
        if (e.key === '-' || e.key === '+' || e.key === 'e' || e.key === 'E') {
            e.preventDefault();
        }
    });
}

/**
 * Initialize validation for all quantity inputs on the page
 */
function initializeQuantityValidation() {
    // Find all quantity inputs
    const quantityInputs = document.querySelectorAll('input[type="number"][name="quantity"]');

    quantityInputs.forEach(input => {
        setupQuantityValidation(input);

        // Set min and max attributes
        input.setAttribute('min', MIN_QUANTITY);
        input.setAttribute('max', MAX_QUANTITY_PER_ITEM);
        input.setAttribute('step', '1');
    });
}

/**
 * Validate form before submission
 * @param {HTMLFormElement} form - The form to validate
 * @returns {boolean} - True if valid, false otherwise
 */
function validateCartForm(form) {
    const quantityInputs = form.querySelectorAll('input[type="number"][name="quantity"]');
    let isValid = true;

    quantityInputs.forEach(input => {
        const validation = validateQuantity(input.value);

        if (!validation.isValid) {
            showValidationError(validation.error, input);
            isValid = false;
        }
    });

    return isValid;
}

// Initialize on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeQuantityValidation);
} else {
    initializeQuantityValidation();
}

// Export functions for use in other scripts
window.validateQuantity = validateQuantity;
window.showValidationError = showValidationError;
window.clearValidationError = clearValidationError;
window.setupQuantityValidation = setupQuantityValidation;
window.validateCartForm = validateCartForm;
