# API Endpoints & Views Documentation

## Overview

This document details all API endpoints and views in the Alwesam-Talabat platform. The application uses Django's URL routing with function-based views.

---

## URL Structure

### Root URL Configuration

```python
# project/urls.py
urlpatterns = [
    path('admin/', admin.site.urls),                    # Django admin
    path('', include('home.urls')),                     # Homepage
    path('products/', include('products.urls')),        # Products
    path('cart/', include('cart.urls')),                # Shopping cart
    path('orders/', include('orders.urls')),            # Orders
    path('accounts/', include('accounts.urls')),        # User accounts
    path('admin-panel/', include('home.admin_urls')),   # Custom admin panel
]
```

---

## Accounts App Endpoints

### Base URL: `/accounts/`

#### User Authentication

##### **Signup**

- **URL**: `/accounts/signup/`
- **Name**: `accounts:signup`
- **Method**: `GET`, `POST`
- **Authentication**: Not required
- **View**: `signup_view`

**POST Request**:

```json
{
    "username": "string",
    "email": "string",
    "phone": "string",
    "address": "string",
    "password1": "string",
    "password2": "string"
}
```

**Response**:

- Success: Redirect to `accounts:pending_approval`
- Error: Re-render form with validation errors

**Notes**:

- New users are created with `is_active=False`
- Requires admin approval before login

---

##### **Login**

- **URL**: `/accounts/login/`
- **Name**: `accounts:login`
- **Method**: `GET`, `POST`
- **Authentication**: Not required
- **Rate Limit**: 5 requests/minute per IP
- **View**: `login_view`

**POST Request**:

```json
{
    "email": "string (email or phone)",
    "password": "string"
}
```

**Response**:

- Success: Redirect to `next` parameter or homepage
- Inactive account: Warning message + re-render login
- Invalid credentials: Error message + re-render login

**Features**:

- Dual authentication (email or phone)
- Custom authentication backend
- Cart synchronization on login
- Rate limiting via `@ratelimit` decorator

---

##### **Logout**

- **URL**: `/accounts/logout/`
- **Name**: `accounts:logout`
- **Method**: `GET`
- **Authentication**: Not required
- **View**: `logout_view`

**Response**: Redirect to homepage with success message

---

##### **Pending Approval**

- **URL**: `/accounts/pending/`
- **Name**: `accounts:pending_approval`
- **Method**: `GET`
- **Authentication**: Not required
- **View**: `pending_approval_view`

**Purpose**: Displayed to users awaiting admin approval

---

#### User Profile

##### **View Profile**

- **URL**: `/accounts/profile/`
- **Name**: `accounts:profile`
- **Method**: `GET`
- **Authentication**: Required (`@login_required`)
- **View**: `profile_view`

**Response Context**:

```python
{
    'user': CustomUser,
    'recent_orders': QuerySet[Order]  # Last 5 orders
}
```

---

##### **Update Profile**

- **URL**: `/accounts/update-profile/`
- **Name**: `accounts:update_profile`
- **Method**: `GET`, `POST`
- **Authentication**: Required (`@login_required`)
- **View**: `update_profile`

**POST Request**:

```json
{
    "username": "string",
    "email": "string",
    "phone": "string",
    "address": "string"
}
```

**Response**:

- Success: Redirect to profile with success message
- Error: Re-render form with validation errors

---

#### Theme & Language

##### **Set Theme**

- **URL**: `/accounts/set-theme/`
- **Name**: `accounts:set_theme`
- **Method**: `POST`
- **Authentication**: Not required
- **View**: `set_theme`

**POST Request (JSON)**:

```json
{
    "theme": "theme-light" | "theme-dark"
}
```

**Response (JSON)**:

```json
{
    "success": true,
    "theme": "theme-light"
}
```

---

##### **Set Language**

- **URL**: `/accounts/set-language/`
- **Name**: `accounts:set_language`
- **Method**: `POST`
- **Authentication**: Not required
- **View**: `set_language`

**POST Request (JSON)**:

```json
{
    "language": "ar" | "en"
}
```

**Response (JSON)**:

```json
{
    "success": true,
    "language": "ar"
}
```

---

##### **Get Theme**

- **URL**: `/accounts/get-theme/`
- **Name**: `accounts:get_theme`
- **Method**: `GET`
- **Authentication**: Not required
- **View**: `get_theme`

**Response (JSON)**:

```json
{
    "theme": "theme-light"
}
```

---

##### **Get Language**

- **URL**: `/accounts/get-language/`
- **Name**: `accounts:get_language`
- **Method**: `GET`
- **Authentication**: Not required
- **View**: `get_language`

**Response (JSON)**:

```json
{
    "language": "ar"
}
```

---

## Products App Endpoints

### Base URL: `/products/`

##### **All Categories**

- **URL**: `/products/`
- **Name**: `products:all_categories`
- **Method**: `GET`
- **Authentication**: Not required
- **View**: `all_categories`

**Response Context**:

```python
{
    'categories': QuerySet[Category]
}
```

---

##### **Category Products**

- **URL**: `/products/category/<slug:slug>/`
- **Name**: `products:category_products`
- **Method**: `GET`
- **Authentication**: Not required
- **View**: `category_products`

**Response Context**:

```python
{
    'category': Category,
    'products': QuerySet[Product]
}
```

---

##### **Product Detail**

- **URL**: `/products/product/<slug:slug>/`
- **Name**: `products:product_detail`
- **Method**: `GET`
- **Authentication**: Not required
- **View**: `product_detail`

**Response Context**:

```python
{
    'product': Product,
    'product_images': QuerySet[ProductImages],
    'variants': QuerySet[ProductVariant],
    'related_products': QuerySet[Product]  # Max 4
}
```

---

##### **Search Products**

- **URL**: `/products/search/`
- **Name**: `products:search`
- **Method**: `GET`
- **Authentication**: Not required
- **View**: `search_products`

**Query Parameters**:

- `q`: Search query string

**Response Context**:

```python
{
    'products': QuerySet[Product],
    'query': str,
    'count': int
}
```

**Search Fields**: Product name, description, category name

---

## Cart App Endpoints

### Base URL: `/cart/`

##### **View Cart**

- **URL**: `/cart/`
- **Name**: `cart:cart_view`
- **Method**: `GET`
- **Authentication**: Required (`@login_required`)
- **View**: `cart_view`

**Response Context**:

```python
{
    'cart': Cart,
    'cart_items': QuerySet[CartItem],
    'total_items': int,
    'total_cartons': int,
    'total_pieces': int
}
```

---

##### **Add to Cart**

- **URL**: `/cart/add/<int:product_id>/`
- **Name**: `cart:add_to_cart`
- **Method**: `POST`
- **Authentication**: Required (`@login_required`)
- **View**: `add_to_cart`

**POST Request (JSON)**:

```json
{
    "variant_id": int,           // Optional
    "color_name": "string",      // Optional
    "size_name": "string",       // Optional
    "quantity": int,             // In selected unit
    "unit_type": "piece" | "carton"
}
```

**Response (JSON)**:

```json
{
    "success": true,
    "message": "تم إضافة المنتج إلى السلة",
    "cart_count": int
}
```

**Validation**:

- Checks product availability
- Validates variant if provided
- Converts quantity to pieces for storage
- Enforces maximum quantity limit

---

##### **Remove from Cart**

- **URL**: `/cart/remove/<int:item_id>/`
- **Name**: `cart:remove_from_cart`
- **Method**: `POST`
- **Authentication**: Required (`@login_required`)
- **View**: `remove_from_cart`

**Response (JSON)**:

```json
{
    "success": true,
    "message": "تم حذف المنتج من السلة"
}
```

---

##### **Update Cart Item**

- **URL**: `/cart/update/<int:item_id>/`
- **Name**: `cart:update_cart_item`
- **Method**: `POST`
- **Authentication**: Required (`@login_required`)
- **View**: `update_cart_item`

**POST Request (JSON)**:

```json
{
    "quantity": int,  // In the original unit type
    "action": "increase" | "decrease" | "set"
}
```

**Response (JSON)**:

```json
{
    "success": true,
    "message": "تم تحديث الكمية"
}
```

---

##### **Sync Cart from LocalStorage**

- **URL**: `/cart/sync/`
- **Name**: `cart:sync_cart`
- **Method**: `POST`
- **Authentication**: Required (`@login_required`)
- **View**: `sync_cart_from_local`

**POST Request (JSON)**:

```json
{
    "cart_items": [
        {
            "product_id": int,
            "variant_id": int,      // Optional
            "size_name": "string",  // Optional
            "quantity": int,
            "unit_type": "piece" | "carton"
        }
    ]
}
```

**Response (JSON)**:

```json
{
    "success": true,
    "message": "تم مزامنة السلة بنجاح"
}
```

**Purpose**: Called when user logs in to merge guest cart with user cart

---

##### **Checkout**

- **URL**: `/cart/checkout/`
- **Name**: `cart:checkout`
- **Method**: `GET`
- **Authentication**: Required (`@login_required`)
- **View**: `checkout`

**Response Context**:

```python
{
    'cart': Cart,
    'cart_items': QuerySet[CartItem],
    'user': CustomUser
}
```

---

## Orders App Endpoints

### Base URL: `/orders/`

##### **Order List**

- **URL**: `/orders/`
- **Name**: `orders:order_list`
- **Method**: `GET`
- **Authentication**: Required (`@login_required`)
- **View**: `order_list`

**Response Context**:

```python
{
    'orders': QuerySet[Order]  # User's orders, newest first
}
```

---

##### **Order Detail**

- **URL**: `/orders/<int:order_id>/`
- **Name**: `orders:order_detail`
- **Method**: `GET`
- **Authentication**: Required (`@login_required`)
- **View**: `order_detail`

**Response Context**:

```python
{
    'order': Order,
    'total_items': int,
    'total_cartons': int,
    'total_pieces': int
}
```

---

##### **Create Order**

- **URL**: `/orders/create/`
- **Name**: `orders:create_order`
- **Method**: `POST`
- **Authentication**: Required (`@login_required`)
- **View**: `create_order`

**POST Request**:

```json
{
    "phone_number": "string",
    "address": "string",
    "notes": "string"  // Optional
}
```

**Response**:

- Success: Redirect to order detail
- Error: Redirect to checkout with error message

**Process**:

1. Validates cart is not empty
2. Creates order with provided details
3. Converts cart items to order items (preserves variant info)
4. Clears user's cart
5. Returns order confirmation

---

##### **Cancel Order**

- **URL**: `/orders/<int:order_id>/cancel/`
- **Name**: `orders:cancel_order`
- **Method**: `POST`
- **Authentication**: Required (`@login_required`)
- **View**: `cancel_order`

**Response**: Redirect to order detail with status message

**Validation**:

- Only `pending` orders can be cancelled

---

## Home App Endpoints

### Base URL: `/`

##### **Homepage**

- **URL**: `/`
- **Name**: `home:home`
- **Method**: `GET`
- **Authentication**: Not required
- **View**: `home_view`

**Purpose**: Landing page with featured products/categories

---

## Admin Panel Endpoints

### Base URL: `/admin-panel/`

**Authentication**: All endpoints require staff login (`@staff_member_required`)

##### **Dashboard**

- **URL**: `/admin-panel/`
- **Method**: `GET`
- **View**: `admin_dashboard`

**Response Context**:

```python
{
    'total_products': int,
    'total_categories': int,
    'total_orders': int,
    'pending_orders': int,
    'total_users': int,
    'pending_users': int
}
```

---

##### **Manage Products**

- **URL**: `/admin-panel/products/`
- **Method**: `GET`
- **View**: `admin_products`
- **Query Parameters**: `search` (optional)

**Response Context**:

```python
{
    'products': QuerySet[Product],
    'search_query': str
}
```

---

##### **Add Product**

- **URL**: `/admin-panel/products/add/`
- **Method**: `GET`, `POST`
- **View**: `admin_product_add`

**POST Request**: Multipart form data with:

- Product details
- Main image
- Additional images (multiple)
- Variant data (if applicable)

---

##### **Edit Product**

- **URL**: `/admin-panel/products/edit/<int:product_id>/`
- **Method**: `GET`, `POST`
- **View**: `admin_product_edit`

---

##### **Delete Product**

- **URL**: `/admin-panel/products/delete/<int:product_id>/`
- **Method**: `POST`
- **View**: `admin_product_delete`

---

##### **Manage Orders**

- **URL**: `/admin-panel/orders/`
- **Method**: `GET`
- **View**: `admin_orders`
- **Query Parameters**: `search`, `status` (optional)

**Response Context**:

```python
{
    'orders': QuerySet[Order],
    'search_query': str,
    'status_filter': str
}
```

---

##### **Order Detail (Admin)**

- **URL**: `/admin-panel/orders/<int:order_id>/`
- **Method**: `GET`, `POST`
- **View**: `admin_order_detail`

**POST**: Update order status

---

##### **Manage Categories**

- **URL**: `/admin-panel/categories/`
- **Method**: `GET`
- **View**: `admin_categories`

---

##### **Add Category**

- **URL**: `/admin-panel/categories/add/`
- **Method**: `GET`, `POST`
- **View**: `admin_category_add`

---

##### **Edit Category**

- **URL**: `/admin-panel/categories/edit/<int:category_id>/`
- **Method**: `GET`, `POST`
- **View**: `admin_category_edit`

---

##### **Delete Category**

- **URL**: `/admin-panel/categories/delete/<int:category_id>/`
- **Method**: `POST`
- **View**: `admin_category_delete`

---

##### **Pending Users**

- **URL**: `/admin-panel/users/pending/`
- **Method**: `GET`
- **View**: `admin_pending_users`

**Response Context**:

```python
{
    'pending_users': QuerySet[CustomUser]
}
```

---

##### **All Users**

- **URL**: `/admin-panel/users/`
- **Method**: `GET`
- **View**: `admin_all_users`
- **Query Parameters**: `search`, `status` (all/active/inactive)

---

##### **Approve User**

- **URL**: `/admin-panel/users/approve/<int:user_id>/`
- **Method**: `POST`
- **View**: `admin_approve_user`

**Action**: Sets `is_active=True`

---

##### **Reject User**

- **URL**: `/admin-panel/users/reject/<int:user_id>/`
- **Method**: `POST`
- **View**: `admin_reject_user`

**Action**: Deletes user account

---

##### **Toggle User Status**

- **URL**: `/admin-panel/users/toggle/<int:user_id>/`
- **Method**: `POST`
- **View**: `admin_toggle_user_status`

**Action**: Toggles `is_active` status

---

## Rate Limiting

### Configured Limits

- **Login**: 5 attempts per minute (per IP)
- **Cart Operations**: 30 requests per minute (per user)

### Implementation

Uses `django-ratelimit` with IP-based and user-based keys

---

## Error Responses

### Standard Error Codes

- **400**: Bad Request (invalid data)
- **401**: Unauthorized (login required)
- **403**: Forbidden (permission denied)
- **404**: Not Found (resource doesn't exist)
- **500**: Internal Server Error

### Error Pages

- Custom **404** template
- Custom **500** template

---

## API Best Practices

### Request Headers

```http
Content-Type: application/json
X-CSRFToken: <csrf_token>  # For POST requests
```

### CSRF Protection

All POST requests require CSRF token:

- Forms: Automatically included via `{% csrf_token %}`
- AJAX: Include token in `X-CSRFToken` header

### Response Format

JSON responses follow this structure:

```json
{
    "success": true | false,
    "message": "string",
    "data": {}  // Optional
}
```
