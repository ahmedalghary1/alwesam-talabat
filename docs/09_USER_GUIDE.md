# User Guide

## Welcome to Alwesam-Talabat

This guide will help you use the Alwesam-Talabat e-commerce platform effectively. Whether you're a new user or returning customer, you'll find everything you need to browse products, place orders, and manage your account.

---

## Getting Started

### System Requirements

- **Web Browser**: Chrome, Firefox, Safari, or Edge (latest version recommended)
- **Internet Connection**: Stable connection for best experience
- **Device**: Desktop, tablet, or mobile phone

### Accessing the Platform

Visit the website at: **[Your Domain URL]**

---

## Creating an Account

### Step 1: Registration

1. Click **"التسجيل"** (Sign Up) in the navigation bar
2. Fill in the registration form:
   - **Username**: Choose a unique username
   - **Email**: Your valid email address
   - **Phone Number**: Your contact number
   - **Address**: Your delivery address
   - **Password**: Choose a strong password
   - **Confirm Password**: Re-enter your password
3. Click **"إنشاء حساب"** (Create Account)

### Step 2: Account Approval

- Your account will be created but **not active** immediately
- You'll see a message: *"حسابك في انتظار موافقة المسؤول"*
- Wait for admin approval (usually within 24 hours)
- Once approved, you'll be able to log in

> **Note**: This approval step ensures security and prevents spam accounts.

---

## Logging In

### Login Process

1. Click **"تسجيل الدخول"** (Login) in the navigation bar
2. Enter your **Email** or **Phone Number**
3. Enter your **Password**
4. Click **"دخول"** (Login)

### If Login Fails

- **Incorrect credentials**: Check your email/phone and password
- **Account pending**: Your account hasn't been approved yet
- **Account deactivated**: Contact admin for reactivation

### Forgot Password

(Currently not implemented - contact admin for password reset)

---

## Browsing Products

### Homepage

The homepage displays:

- **Hero Slider**: Featured promotions
- **Product Categories**: Quick access to different sections
- **Featured Products**: Highlighted items

### Viewing Categories

1. Click **"المنتجات"** (Products) in the navigation bar
2. Browse all available categories
3. Click on any category to view its products

### Product Details

1. Click on any product card
2. View product information:
   - Product name and description
   - Product images (main + gallery)
   - Pieces per carton (عدد القطع في الكرتونة)
   - Availability status
   - Available variants (colors/sizes if applicable)
3. See related products at the bottom

---

## Searching for Products

### Using the Search Feature

1. Find the search bar in the navigation
2. Type your search query (product name, description, or category)
3. Press Enter or click the search icon
4. Browse search results
5. Click on any product to view details

---

## Adding Products to Cart

### For Products Without Variants

1. On the product detail page
2. Select **Quantity**:
   - Choose unit type: **قطعة** (Pieces) or **كرتونة** (Cartons)
   - Enter desired quantity
3. Click **"أضف إلى السلة"** (Add to Cart)
4. See success message and updated cart count

### For Products With Variants

1. On the product detail page
2. **Select Color** (if available):
   - Click on color option
   - Selected color will be highlighted
3. **Select Size** (if available):
   - Choose from size dropdown
4. Select **Quantity**
5. Click **"أضف إلى السلة"** (Add to Cart)

> **Important**: You must select a color/size if variants exist, otherwise you'll see an error message.

---

## Managing Your Cart

### Viewing Cart

1. Click the **cart icon** in the navigation (shows item count)
2. Or navigate to `/cart/`
3. View all items in your cart with:
   - Product image and name
   - Variant details (color, size)
   - Quantity (in pieces and cartons)
   - Unit type

### Updating Quantities

- **Increase**: Click the **+** button
- **Decrease**: Click the **-** button
- **Remove**: Click the **🗑️** (delete) button
- Confirm deletion when prompted

### Cart Summary

The cart page shows:

- **Total Items**: Number of different products
- **Total Cartons**: Total in cartons
- **Total Pieces**: Total in pieces

---

## Placing an Order

### Checkout Process

1. From your cart, click **"إتمام الطلب"** (Proceed to Checkout)
2. Review your order items
3. Confirm or update delivery information:
   - **Phone Number**: Auto-filled from your profile
   - **Delivery Address**: Auto-filled from your profile
   - **Order Notes**: Optional special instructions
4. Click **"تأكيد الطلب"** (Confirm Order)
5. Your order is created!

### After Order Placement

- You'll be redirected to the order details page
- Order status: **"قيد الانتظار"** (Pending)
- Your cart will be emptied
- You'll receive an order number (Order ID)

---

## Tracking Your Orders

### Viewing Order History

1. Click your **username** in the navigation
2. Select **"طلباتي"** (My Orders) or navigate to `/orders/`
3. See list of all your orders with:
   - Order ID
   - Order date
   - Status
   - Total items

### Order Details

1. Click on any order to view full details
2. See:
   - Order status badge
   - Customer information
   - Delivery address
   - All order items with quantities
   - Order notes
   - Order timeline

### Order Status Types

| Status | Arabic | Description |
|--------|--------|-------------|
| Pending | قيد الانتظار | Order received, awaiting confirmation |
| Confirmed | تم التأكيد | Order confirmed by admin |
| Shipped | تم الشحن | Order shipped for delivery |
| Delivered | تم التسليم | Order successfully delivered |
| Cancelled | تم الإلغاء | Order cancelled |

### Cancelling an Order

- You can only cancel **Pending** orders
- Click **"إلغاء الطلب"** (Cancel Order) button
- Confirm cancellation
- Order status changes to **Cancelled**

---

## Managing Your Profile

### Viewing Profile

1. Click your **username** in navigation
2. Select **"الملف الشخصي"** (Profile)
3. View your:
   - Personal information
   - Recent orders (last 5)

### Updating Profile

1. From profile page, click **"تعديل الملف الشخصي"** (Edit Profile)
2. Update information:
   - Username
   - Email
   - Phone number
   - Address
3. Click **"حفظ التغييرات"** (Save Changes)

---

## Theme & Language Settings

### Changing Theme

1. Find the **theme icon** (🌙/☀️) in the navigation
2. Click to toggle between:
   - **Light mode** (النمط الفاتح)
   - **Dark mode** (النمط الداكن)
3. Your preference is saved automatically

### Changing Language

(This feature requires implementation)

- Currently, the platform is in Arabic
- English support planned for future

---

## Tips for Best Experience

### Shopping Tips

1. **Check Availability**: Look for the availability status on product pages
2. **Review Product Details**: Check pieces per carton before ordering
3. **Choose Correct Variant**: Ensure you select the right color/size
4. **Double-Check Cart**: Review your cart before checkout
5. **Provide Accurate Info**: Ensure your address and phone are correct

### Account Security

1. **Strong Password**: Use a secure password with letters, numbers, and symbols
2. **Keep Info Updated**: Update your profile if contact details change
3. **Logout**: Always logout on shared devices
4. **Don't Share**: Never share your login credentials

---

## Frequently Asked Questions (FAQ)

**Q: How long does account approval take?**
A: Usually within 24 hours. Contact admin if longer.

**Q: Can I edit my order after placing it?**
A: No, but you can cancel pending orders and place a new one.

**Q: What is the difference between pieces and cartons?**
A: Products are sold by the carton. Each carton contains a specific number of pieces (usually 24). You can order in either unit.

**Q: Can I have multiple delivery addresses?**
A: Currently, only one primary address is supported in your profile.

**Q: How do I reset my password?**
A: Contact admin for password reset assistance.

**Q: Can I reorder from past orders?**
A: Currently, you need to manually add items again. A "reorder" feature is planned.

**Q: What if a product shows "not available"?**
A: The product is out of stock. Check back later or contact admin.

**Q: Can I order products from different categories together?**
A: Yes! Add products from any categories to your cart and checkout together.

---

## Troubleshooting

### Common Issues

**Problem**: Can't log in
**Solutions**:

- Check email/phone spelling
- Verify password is correct
- Ensure account has been approved by admin
- Try clearing browser cache

**Problem**: Cart shows wrong quantity
**Solutions**:

- Refresh the page
- Check if you selected pieces or cartons
- Update quantity manually

**Problem**: Can't add product to cart
**Solutions**:

- Ensure you're logged in
- Check if color/size is selected (for variant products)
- Verify product is available
- Try refreshing the page

**Problem**: Images not loading
**Solutions**:

- Check internet connection
- Refresh the page (Ctrl+F5)
- Try clearing browser cache
- Try a different browser

**Problem**: Page not loading
**Solutions**:

- Check internet connection
- Wait a moment and refresh
- Clear browser cache
- Contact support if persists

---

## Getting Help

### Contact Information

- **Email**: [support email]
- **Phone**: [support phone]
- **Business Hours**: [operating hours]

### Support Options

1. Email support for account issues
2. Phone support for urgent matters
3. Check FAQ section first

---

## Mobile Usage

### Mobile-Friendly Features

- Responsive design works on all devices
- Touch-friendly buttons and navigation
- Optimized images for faster loading
- Simplified navigation menu on mobile

### Best Practices on Mobile

- Use portrait mode for best experience
- Tap and hold to zoom images
- Swipe left/right in image galleries
- Use WiFi for faster loading

---

## Conclusion

Thank you for using Alwesam-Talabat! We hope this guide helps you navigate the platform easily.

**Happy Shopping! 🛒**

For additional support or questions not covered here, please don't hesitate to contact our support team.

---

*Last Updated: December 2025*
