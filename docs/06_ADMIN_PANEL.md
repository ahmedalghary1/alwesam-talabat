# Admin Panel Documentation

## Overview

The Alwesam-Talabat platform includes a custom-built admin panel separate from Django's default admin. This panel provides a user-friendly interface for managing products, categories, orders, and users.

**Base URL**: `/admin-panel/`

---

## Access Control

### Requirements

- User must be a staff member (`is_staff=True`)
- All admin views use `@staff_member_required` decorator
- Automatic redirect to login if not authenticated

### Staff User Creation

```bash
# Via Django shell
python manage.py shell
>>> from accounts.models import CustomUser
>>> user = CustomUser.objects.get(email='user@example.com')
>>> user.is_staff = True
>>> user.save()

# Or create superuser
python manage.py createsuperuser
```

---

## Dashboard

### URL: `/admin-panel/`

### Features

Displays key statistics and metrics:

**Metrics Displayed**:

- Total Products
- Total Categories
- Total Orders
- Pending Orders
- Total Users (active)
- Pending Users (awaiting approval)

**Quick Actions**:

- View all products
- View all orders
- View pending users
- Add new product
- Add new category

---

## Product Management

### View All Products

**URL**: `/admin-panel/products/`

**Features**:

- **List View**: Grid/table of all products
- **Search**: Search by product name
- **Status Indicator**: Shows availability status
- **Quick Actions**: Edit, Delete buttons

**Search Implementation**:

```python
def admin_products(request):
    search_query = request.GET.get('search', '')
    products = Product.objects.all()
    
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    return render(request, 'admin/products.html', {
        'products': products,
        'search_query': search_query
    })
```

---

### Add Product

**URL**: `/admin-panel/products/add/`

**Form Fields**:

#### Basic Information

- **Name**: Product name (required)
- **Description**: Full product description (optional)
- **Category**: Dropdown selection (required)
- **Pieces per Carton**: Default 24 (required)
- **Availability**: Checkbox for stock status

#### Images

- **Main Image**: Primary product image (required)
- **Additional Images**: Multiple file upload (optional)

#### Variants

**If product has variants**:

- **Variant Type**: Currently supports "Color"
- **Variant Name**: Display name
- **Variant Code/SKU**: Unique identifier (optional)
- **Variant PCS/Carton**: Override default (optional)
- **Variant Image**: Variant-specific image (optional)
- **Color Selection**: Choose from predefined colors
- **Size Selection**: Multi-select from predefined sizes

**Workflow**:

1. Fill basic product information
2. Upload main image
3. Optionally add additional images
4. If variants needed:
   - Select variant type (Color)
   - Fill variant details
   - Select color
   - Select applicable sizes
   - Upload variant images
5. Submit form
6. Product created with slug auto-generated

---

### Edit Product

**URL**: `/admin-panel/products/edit/<product_id>/`

**Features**:

- Pre-populated form with existing data
- Update product information
- Manage additional images:
  - View existing images
  - Delete individual images
  - Add new images
- Manage variants:
  - Edit existing variants
  - Add new variants
  - Delete variants
- Update variant images

**Image Management**:

```html
<!-- Existing images displayed with delete option -->
<div class="image-gallery">
    {% for image in product_images %}
    <div class="image-item">
        <img src="{{ image.image.url }}" alt="">
        <button type="button" onclick="deleteImage({{ image.id }})">
            حذف
        </button>
    </div>
    {% endfor %}
</div>
```

---

### Delete Product

**URL**: `/admin-panel/products/delete/<product_id>/`

**Method**: POST (with CSRF protection)

**Confirmation**: Requires user confirmation before deletion

**Cascade Effects**:

- Deletes all product images
- Deletes all product variants
- Removes from cart items (SET_NULL in OrderItems)

---

## Category Management

### View All Categories

**URL**: `/admin-panel/categories/`

**Features**:

- List of all categories
- Category image preview
- Product count per category
- Edit/Delete actions

---

### Add Category

**URL**: `/admin-panel/categories/add/`

**Form Fields**:

- **Name**: Category name (required)
- **Description**: Category description (optional)
- **Image**: Category image (required)

**Process**:

- Slug auto-generated from name
- Image automatically compressed
- Redirects to categories list on success

---

### Edit Category

**URL**: `/admin-panel/categories/edit/<category_id>/`

**Features**:

- Update name, description
- Replace category image
- Update existing category

---

### Delete Category

**URL**: `/admin-panel/categories/delete/<category_id>/`

**Method**: POST

**Effect**: Sets `category=NULL` for associated products

---

## Order Management

### View All Orders

**URL**: `/admin-panel/orders/`

**Features**:

#### Filters

- **Status Filter**:
  - All
  - Pending
  - Confirmed
  - Shipped
  - Delivered
  - Cancelled

#### Search

Searches across:

- Order ID
- Customer name
- Customer phone
- Product names in order

**Implementation**:

```python
def admin_orders(request):
    orders = Order.objects.all()
    
    # Status filter
    status = request.GET.get('status')
    if status:
        orders = orders.filter(status=status)
    
    # Search
    search = request.GET.get('search')
    if search:
        orders = orders.filter(
            Q(id__icontains=search) |
            Q(user__username__icontains=search) |
            Q(phone_number__icontains=search) |
            Q(items__product__name__icontains=search)
        ).distinct()
    
    return render(request, 'admin/orders.html', {'orders': orders})
```

#### Display Information

For each order:

- Order ID
- Customer name
- Order date
- Status badge (color-coded)
- Total items
- Quick actions (View details)

---

### Order Detail (Admin)

**URL**: `/admin-panel/orders/<order_id>/`

**View Mode**: Displays complete order information

- Customer details (name, email, phone, address)
- Order items with:
  - Product name
  - Variant info (color, size)
  - Quantity (pieces/cartons)
  - Unit type
- Order notes
- Order timeline

**Edit Mode**: Update order status

- Status dropdown with 5 options
- Update button
- Status change logged

**Status Options**:

1. **قيد الانتظار** (Pending)
2. **تم التأكيد** (Confirmed)
3. **تم الشحن** (Shipped)
4. **تم التسليم** (Delivered)
5. **تم الإلغاء** (Cancelled)

---

## User Management

### Pending Users

**URL**: `/admin-panel/users/pending/`

**Purpose**: Review and approve new user registrations

**Display**:

- Username
- Email
- Phone
- Registration date
- Actions: Approve, Reject

**Approve Action**:

```python
def admin_approve_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.is_active = True
    user.save()
    messages.success(request, f'تم قبول المستخدم {user.username}')
    return redirect('home:admin_pending_users')
```

**Reject Action**:

```python
def admin_reject_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.delete()
    messages.success(request, 'تم رفض المستخدم')
    return redirect('home:admin_pending_users')
```

---

### All Users

**URL**: `/admin-panel/users/`

**Features**:

#### Filters

- All users
- Active users only
- Inactive users only

#### Search

Search by:

- Username
- Email
- Phone number

#### Display Information

- Username
- Email
- Phone
- Status (Active/Inactive)
- Staff status
- Registration date

#### Actions

- **Toggle Status**: Activate/Deactivate user
- **View Profile**: (Future feature)

**Toggle Status**:

```python
def admin_toggle_user_status(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.is_active = not user.is_active
    user.save()
    
    status = "تفعيل" if user.is_active else "إيقاف"
    messages.success(request, f'تم {status} حساب {user.username}')
    return redirect('home:admin_all_users')
```

---

## Search Functionality

### Global Search Features

#### Product Search

- Product name
- Product description
- Category name

#### Order Search

- Order ID (exact or partial)
- Customer username
- Customer phone number
- Product names in order items

#### User Search

- Username
- Email address
- Phone number

### Search Implementation Pattern

```python
# Case-insensitive substring match using icontains
objects.filter(
    Q(field1__icontains=query) |
    Q(field2__icontains=query) |
    Q(field3__icontains=query)
).distinct()
```

---

## UI/UX Features

### Dashboard Design

- **Clean Layout**: Card-based metrics display
- **Color-Coded**: Different colors for different metric types
- **Responsive**: Works on desktop and tablet
- **Quick Links**: Direct navigation to main sections

### Data Tables

- **Sortable Headers**: (Future enhancement)
- **Pagination**: For large datasets (Future enhancement)
- **Row Actions**: Edit/Delete buttons
- **Status Badges**: Visual status indicators

### Forms

- **Validation**: Client and server-side
- **Error Display**: Clear error messages
- **Required Fields**: Marked with asterisk
- **Help Text**: Tooltips and descriptions
- **Image Preview**: Preview uploaded images

### Confirmation Modals

- Delete operations require confirmation
- Prevents accidental deletions
- Clear messaging about consequences

---

## Security Measures

### Authorization

```python
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def admin_dashboard(request):
    # Only accessible to staff members
    pass
```

### CSRF Protection

All forms include CSRF tokens:

```html
<form method="post">
    {% csrf_token %}
    <!-- form fields -->
</form>
```

### Input Validation

- Server-side validation on all forms
- Sanitization of user inputs
- File type validation for image uploads
- Size limits on uploads

---

## Permissions Matrix

| Feature | Staff | Superuser |
|---------|-------|-----------|
| View Dashboard | ✅ | ✅ |
| Manage Products | ✅ | ✅ |
| Manage Categories | ✅ | ✅ |
| View Orders | ✅ | ✅ |
| Update Order Status | ✅ | ✅ |
| Approve Users | ✅ | ✅ |
| Manage Users | ✅ | ✅ |
| Access Django Admin | ❌ | ✅ |

---

## Admin Workflows

### Approve New User Workflow

```
1. Admin receives notification (pending users count)
2. Navigate to /admin-panel/users/pending/
3. Review user details
4. Click "Approve" → User.is_active = True
5. User can now log in
```

### Process Order Workflow

```
1. View pending orders in dashboard
2. Navigate to /admin-panel/orders/?status=pending
3. Click order to view details
4. Review order items and customer info
5. Update status: Pending → Confirmed → Shipped → Delivered
6. Order status updated, customer sees updated status
```

### Add Product with Variants Workflow

```
1. Navigate to /admin-panel/products/add/
2. Fill product basic info
3. Upload main product image
4. Add product variants:
   - Select variant type (Color)
   - Enter variant details
   - Select color from dropdown
   - Select applicable sizes
   - Upload variant-specific images
5. Submit form
6. Product created with all variants
```

---

## Future Enhancements

### Planned Features

- [ ] Bulk actions (delete multiple, update status)
- [ ] Export orders to CSV/Excel
- [ ] Advanced analytics dashboard
- [ ] Email notifications for status changes
- [ ] Inventory management integration
- [ ] Sales reports and charts
- [ ] Customer communication tools
- [ ] Activity logs and audit trail
- [ ] Role-based permissions (beyond staff/superuser)

---

## Troubleshooting

### Common Issues

**Issue**: Can't access admin panel
**Solution**: Ensure user has `is_staff=True` set

**Issue**: Images not uploading
**Solution**: Check `MEDIA_ROOT` and file permissions

**Issue**: Search not working
**Solution**: Verify database supports case-insensitive lookups

**Issue**: Product variants not saving
**Solution**: Check form validation errors in Django logs
