# Frontend Components & Technologies Documentation

## Overview

The frontend is built with vanilla HTML, CSS, and JavaScript, following a modular and responsive design approach with RTL (right-to-left) support for Arabic.

---

## Template Architecture

### Base Template

**File**: `templates/base.html`

**Key Features**:

- Responsive navigation bar
- Theme toggle (light/dark)
- Language switcher (Arabic/English)
- Cart counter (global)
- Footer with site information
- Dynamic content blocks
- CSRF token management

**Template Blocks**:

```django
{% block title %}Default Title{% endblock %}
{% block extra_css %}<!-- Page-specific CSS -->{% endblock %}
{% block content %}<!-- Main content -->{% endblock %}
{% block extra_js %}<!-- Page-specific JS -->{% endblock %}
```

### Template Structure

```
templates/
├── base.html                 # Master template
├── 404.html                  # Not found page
├── 500.html                  # Server error page
├── accounts/
│   ├── login.html           # Login page
│   ├── signup.html          # Registration page
│   ├── profile.html         # User profile
│   ├── update_profile.html  # Profile edit
│   └── pending_approval.html
├── products/
│   ├── all_categories.html  # Categories grid
│   ├── categories.html      # Category products
│   ├── product_detail.html  # Product details
│   └── search_results.html  # Search results
├── cart/
│   ├── cart.html            # Cart page
│   └── checkout.html        # Checkout page
├── orders/
│   ├── order_list.html      # Order history
│   └── order_detail.html    # Order details
├── home/
│   └── home.html            # Homepage
└── admin/
    ├── dashboard.html       # Admin dashboard
    ├── products.html        # Product management
    ├── orders.html          # Order management
    ├── categories.html      # Category management
    └── users.html           # User management
```

---

## JavaScript Modules

### 1. Main Script (`script.js`)

**Purpose**: Core functionality and page interactions

**Key Functions**:

#### Theme Management

```javascript
function toggleTheme() {
    const currentTheme = body.classList.contains('theme-dark') ? 
        'theme-light' : 'theme-dark';
    
    fetch('/accounts/set-theme/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({theme: currentTheme})
    });
}
```

#### Language Switching

```javascript
function setLanguage(lang) {
    fetch('/accounts/set-language/', {
        method: 'POST',
        body: JSON.stringify({language: lang})
    }).then(() => location.reload());
}
```

#### Scroll Animations

```javascript
// Intersection Observer for fade-in animations
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('visible');
        } else {
            entry.target.classList.remove('visible');
        }
    });
}, {threshold: 0.1});
```

#### Image Slider

```javascript
// Homepage hero slider functionality
// Auto-advances every 5 seconds
// Supports manual navigation
```

---

### 2. Cart Enhancements (`cart-enhancements.js`)

**Purpose**: Shopping cart functionality and localStorage management

**Key Features**:

#### Add to Cart (Guest Users)

```javascript
function addToCartLocal(productId, variantId, quantity, unitType, sizeName) {
    let cart = JSON.parse(localStorage.getItem('guestCart') || '[]');
    
    // Find or create cart item
    let item = cart.find(i => 
        i.product_id === productId && 
        i.variant_id === variantId &&
        i.size_name === sizeName
    );
    
    if (item) {
        item.quantity += quantity;
    } else {
        cart.push({product_id, variant_id, quantity, unit_type, size_name});
    }
    
    localStorage.setItem('guestCart', JSON.stringify(cart));
    updateCartCount();
}
```

#### Cart Synchronization on Login

```javascript
function syncCartOnLogin() {
    const guestCart = JSON.parse(localStorage.getItem('guestCart') || '[]');
    
    if (guestCart.length > 0) {
        fetch('/cart/sync/', {
            method: 'POST',
            body: JSON.stringify({cart_items: guestCart})
        }).then(() => {
            localStorage.removeItem('guestCart');
            location.reload();
        });
    }
}
```

#### Update Cart Item

```javascript
function updateCartItem(itemId, action) {
    fetch(`/cart/update/${itemId}/`, {
        method: 'POST',
        body: JSON.stringify({action: action})
    }).then(response => response.json())
      .then(data => {
          if (data.success) {
              location.reload();
          }
      });
}
```

#### Remove from Cart

```javascript
function removeFromCart(itemId) {
    if (confirm('هل تريد حذف هذا المنتج من السلة؟')) {
        fetch(`/cart/remove/${itemId}/`, {
            method: 'POST'
        }).then(() => location.reload());
    }
}
```

---

### 3. Validation (`validation.js`)

**Purpose**: Client-side form validation

**Features**:

#### Product Detail Validation

```javascript
// Validates color selection if variants exist
document.querySelector('.add-to-cart-form').addEventListener('submit', (e) => {
    const hasVariants = document.querySelectorAll('.color-option').length > 0;
    const selectedColor = document.querySelector('.color-option.selected');
    
    if (hasVariants && !selectedColor) {
        e.preventDefault();
        alert('الرجاء اختيار اللون');
    }
});
```

#### Form Validation

- Email format validation
- Phone number format validation
- Password strength checking
- Required field validation
- Matching password confirmation

---

## CSS Architecture

### File Organization

```
static/css/
├── base.css                 # Global styles, variables, reset
├── home.css                 # Homepage styles
├── products.css             # Product pages
├── cart.css                 # Cart pages
├── orders.css               # Order pages
├── profile.css              # Profile pages
├── admin.css                # Admin panel
├── auth.css                 # Login/signup forms
├── categories.css           # Category pages
├── product-detail.css       # Product detail page
└── responsive.css           # Media queries
```

### Design System

#### CSS Variables (base.css)

```css
:root {
    /* Colors - Light Theme */
    --primary-color: #2563eb;
    --secondary-color: #3b82f6;
    --background: #ffffff;
    --surface: #f8fafc;
    --text-primary: #1e293b;
    --text-secondary: #64748b;
    --border-color: #e2e8f0;
    --success: #10b981;
    --warning: #f59e0b;
    --error: #ef4444;
    
    /* Spacing */
    --spacing-xs: 0.25rem;
    --spacing-sm: 0.5rem;
    --spacing-md: 1rem;
    --spacing-lg: 1.5rem;
    --spacing-xl: 2rem;
    
    /* Typography */
    --font-primary: 'Cairo', 'Segoe UI', Tahoma, sans-serif;
    --font-size-sm: 0.875rem;
    --font-size-base: 1rem;
    --font-size-lg: 1.125rem;
    --font-size-xl: 1.5rem;
    
    /* Border Radius */
    --radius-sm: 0.375rem;
    --radius-md: 0.5rem;
    --radius-lg: 1rem;
    
    /* Shadows */
    --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
    --shadow-md: 0 4px 6px rgba(0,0,0,0.1);
    --shadow-lg: 0 10px 15px rgba(0,0,0,0.1);
    
    /* Transitions */
    --transition-fast: 150ms ease;
    --transition-base: 300ms ease;
    --transition-slow: 500ms ease;
}
```

#### Dark Theme Variables

```css
body.theme-dark {
    --background: #0f172a;
    --surface: #1e293b;
    --text-primary: #f1f5f9;
    --text-secondary: #94a3b8;
    --border-color: #334155;
    /* ... other dark theme colors */
}
```

### RTL Support

#### Implementation

```css
/* Automatic RTL for Arabic */
body[dir="rtl"] {
    text-align: right;
}

body[dir="rtl"] .container {
    direction: rtl;
}

/* Flip margins/padding */
body[dir="rtl"] .ml-4 {
    margin-left: 0;
    margin-right: 1rem;
}
```

---

## Responsive Design

### Breakpoints

```css
/* Mobile First Approach */
@media (min-width: 640px) { /* sm */ }
@media (min-width: 768px) { /* md */ }
@media (min-width: 1024px) { /* lg */ }
@media (min-width: 1280px) { /* xl */ }
```

### Mobile Optimizations

- Touch-friendly buttons (min 44x44px)
- Simplified navigation
- Stackable grid layouts
- Optimized images
- Reduced animations on mobile

---

## Component Patterns

### Card Component

```html
<div class="card">
    <img src="..." alt="..." class="card-image">
    <div class="card-body">
        <h3 class="card-title">Title</h3>
        <p class="card-text">Description</p>
        <a href="#" class="btn btn-primary">Action</a>
    </div>
</div>
```

### Button Component

```html
<button class="btn btn-primary">Primary</button>
<button class="btn btn-secondary">Secondary</button>
<button class="btn btn-success">Success</button>
<button class="btn btn-danger">Danger</button>
```

### Form Component

```html
<form class="form" method="post">
    {% csrf_token %}
    <div class="form-group">
        <label for="email">Email</label>
        <input type="email" id="email" name="email" class="form-control">
        <span class="form-error">Error message</span>
    </div>
    <button type="submit" class="btn btn-primary">Submit</button>
</form>
```

---

## Static Assets

### Images

```
static/images/
├── logo.svg
├── slider/
│   ├── alwisam_slider.svg
│   ├── 48.png
│   ├── 53.png
│   └── ...
└── placeholders/
```

### Icons

Uses inline SVG icons for:

- Cart icon
- User icon
- Theme toggle (sun/moon)
- Menu icon (mobile)
- Search icon

---

## Performance Optimizations

### Image Optimization

- WebP format support
- Lazy loading: `loading="lazy"`
- Responsive images: `srcset` and `sizes`
- Image compression on upload (server-side)

### JavaScript Optimization

- Defer non-critical scripts
- Event delegation for dynamic content
- Debounced scroll/resize handlers
- Minimal third-party dependencies

### CSS Optimization

- Critical CSS inline
- CSS minification (production)
- Remove unused CSS
- Efficient selectors

---

## Accessibility

### WCAG Guidelines

- ✅ Semantic HTML
- ✅ ARIA labels where needed
- ✅ Keyboard navigation support
- ✅ Focus indicators
- ✅ Sufficient color contrast
- ✅ Alt text for images
- ✅ Form labels properly associated

### Screen Reader Support

```html
<button aria-label="إضافة إلى السلة">
    <svg aria-hidden="true"><!-- icon --></svg>
</button>
```

---

## Browser Support

- Chrome/Edge: Latest 2 versions
- Firefox: Latest 2 versions
- Safari: Latest 2 versions
- Mobile browsers: iOS Safari, Chrome Android

---

## Development Workflow

### Hot Reload (Development)

Django's development server auto-reloads on file changes.

### CSS Development

1. Edit CSS in `static/css/`
2. Hard refresh browser (Ctrl+F5)
3. Check responsive design in DevTools

### JavaScript Development

1. Edit JS in `static/js/`
2. Clear browser cache
3. Test in browser console
4. Validate with ESLint (if configured)

---

## Future Enhancements

### Potential Improvements

- [ ] Migrate to a CSS preprocessor (SASS/LESS)
- [ ] Implement CSS-in-JS for component isolation
- [ ] Add service worker for offline support
- [ ] Implement progressive web app (PWA) features
- [ ] Add skeleton screens for loading states
- [ ] Implement virtual scrolling for large lists
- [ ] Add image gallery lightbox
- [ ] Implement advanced product filters
