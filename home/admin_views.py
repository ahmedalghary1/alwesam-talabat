from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Q, Count
from products.models import Product, Category, ProductImages, ProductVariant, Color, Size
from orders.models import Order


@staff_member_required
def admin_dashboard(request):
    """لوحة تحكم الإدارة"""
    # إحصائيات
    total_products = Product.objects.count()
    total_categories = Category.objects.count()
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()
    
    # آخر الطلبات
    recent_orders = Order.objects.all().order_by('-created_at')[:10]
    
    context = {
        'total_products': total_products,
        'total_categories': total_categories,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'recent_orders': recent_orders,
    }
    return render(request, 'admin/dashboard.html', context)


@staff_member_required
def admin_products(request):
    """إدارة المنتجات"""
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    
    products = Product.objects.all()
    
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    if category_filter:
        products = products.filter(category__slug=category_filter)
    
    categories = Category.objects.all()
    
    return render(request, 'admin/products.html', {
        'products': products,
        'categories': categories,
        'search_query': search_query,
        'category_filter': category_filter,
    })


@staff_member_required
def admin_product_add(request):
    """Add a new product"""
    categories = Category.objects.all()
    colors = Color.objects.all()
    sizes = Size.objects.all()
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        pcs_carton = request.POST.get('pcs_carton', 1)
        category_id = request.POST.get('category')
        image = request.FILES.get('image')
        
        try:
            # Generate slug from name
            from django.utils.text import slugify
            slug = slugify(name, allow_unicode=True)
            
            # Create the product
            product = Product.objects.create(
                name=name,
                slug=slug,
                description=description,
                pcs_carton=pcs_carton,
                category_id=category_id if category_id else None,
                image=image,
                is_available='is_available' in request.POST  # Checkbox only sent if checked
            )
            
            # Handle additional images
            additional_images = request.FILES.getlist('additional_images[]')
            for idx, img in enumerate(additional_images):
                ProductImages.objects.create(product=product, image=img, order=idx)
            
            # Handle product variants with multiple images
            variant_names = request.POST.getlist('variant_name[]')
            variant_codes = request.POST.getlist('variant_code[]')
            variant_pcs = request.POST.getlist('variant_pcs_carton[]')
            variant_available = request.POST.getlist('variant_available[]')
            
            # Get color and size data
            variant_colors = request.POST.getlist('variant_color[]')
            
            for i in range(len(variant_names)):
                if variant_names[i].strip():  # Only create if name is provided
                    # Get color ID for this variant
                    color_id = variant_colors[i] if i < len(variant_colors) and variant_colors[i] else None
                    
                    variant = ProductVariant.objects.create(
                        product=product,
                        name=variant_names[i],
                        code=variant_codes[i] if i < len(variant_codes) and variant_codes[i] else None,
                        variant_type='color',  # Default to color
                        length_label=request.POST.getlist('variant_length_label[]')[i] if i < len(request.POST.getlist('variant_length_label[]')) else None,
                        pcs_carton=int(variant_pcs[i]) if i < len(variant_pcs) and variant_pcs[i] else 24,
                        is_available=str(i) in variant_available,
                        color_id=color_id if color_id else None
                    )
                    
                    # Add sizes to variant (many-to-many)
                    size_ids_key = f'variant_{i}_sizes[]'
                    size_ids = request.POST.getlist(size_ids_key)
                    if size_ids:
                        variant.sizes.set(size_ids)
                    
                    # Save multiple variant images using indexed naming
                    # Images for this variant are in variant_{i}_images[]
                    variant_images_key = f'variant_{i}_images[]'
                    variant_images = request.FILES.getlist(variant_images_key)
                    
                    if variant_images:
                        from products.models import VariantImage
                        for idx, img in enumerate(variant_images):
                            VariantImage.objects.create(
                                variant=variant,
                                image=img,
                                order=idx
                            )
            
            messages.success(request, f'تم إضافة المنتج "{product.name}" بنجاح')
            return redirect('admin_app:admin_products')
        except Exception as e:
            messages.error(request, f'حدث خطأ: {str(e)}')
    
    return render(request, 'admin/product_add.html', {
        'categories': categories,
        'colors': colors,
        'sizes': sizes
    })


@staff_member_required
def admin_product_edit(request, product_id):
    """تعديل منتج موجود"""
    product = get_object_or_404(Product, id=product_id)
    categories = Category.objects.all()
    colors = Color.objects.all()
    sizes = Size.objects.all()
    variants = product.variants.all()  # Get all variants for this product
    
    if request.method == 'POST':
        product.name = request.POST.get('name', product.name)
        product.description = request.POST.get('description', product.description)
        product.pcs_carton = request.POST.get('pcs_carton', product.pcs_carton)
        product.is_available = 'is_available' in request.POST  # Checkbox only sent if checked
        category_id = request.POST.get('category')
        if category_id:
            product.category_id = category_id
        
        if 'image' in request.FILES:
            product.image = request.FILES['image']
        
        product.save()
        
        # Handle product images deletion
        delete_product_images = request.POST.getlist('delete_product_images[]')
        if delete_product_images:
            for img_id in delete_product_images:
                if img_id:
                    try:
                        ProductImages.objects.filter(id=int(img_id), product=product).delete()
                    except (ValueError, ProductImages.DoesNotExist):
                        pass
        
        # Handle new product images addition
        new_product_images = request.FILES.getlist('new_product_images[]')
        if new_product_images:
            from django.db import models as db_models
            max_order = product.additional_images.aggregate(db_models.Max('order'))['order__max'] or -1
            
            for idx, img in enumerate(new_product_images):
                ProductImages.objects.create(
                    product=product,
                    image=img,
                    order=max_order + idx + 1
                )
        
        # Handle variants update
        variant_ids = request.POST.getlist('variant_id[]')
        variant_names = request.POST.getlist('variant_name[]')
        variant_codes = request.POST.getlist('variant_code[]')
        variant_pcs = request.POST.getlist('variant_pcs_carton[]')
        variant_available = request.POST.getlist('variant_available[]') # Changed from variant_stocks
        variant_images = request.FILES.getlist('variant_image[]')
        variant_colors = request.POST.getlist('variant_color[]')
        
        # Track which variants to keep
        updated_variant_ids = []
        
        # Update/Create variants
        for i in range(len(variant_names)):
            if variant_names[i].strip():
                color_id = variant_colors[i] if i < len(variant_colors) and variant_colors[i] else None
                
                variant_data = {
                    'product': product,
                    'name': variant_names[i],
                    'code': variant_codes[i] if variant_codes[i] else None,
                    'length_label': request.POST.getlist('variant_length_label[]')[i] if i < len(request.POST.getlist('variant_length_label[]')) else None,
                    'variant_type': 'color',  # Default to color
                    'pcs_carton': int(variant_pcs[i]) if variant_pcs[i] else 24,
                    'is_available': i < len(variant_available),  # Checkbox sends value only if checked
                    'color_id': color_id if color_id else None
                }
                
                if i < len(variant_ids) and variant_ids[i]:
                    # Update existing
                    variant = ProductVariant.objects.get(id=variant_ids[i], product=product)
                    for key, value in variant_data.items():
                        setattr(variant, key, value)
                    if i < len(variant_images) and variant_images[i]:
                        variant.image = variant_images[i]
                    variant.save()
                    
                    # Update sizes for existing variant
                    size_ids_key = f'variant_{i}_sizes[]'
                    size_ids = request.POST.getlist(size_ids_key)
                    variant.sizes.set(size_ids if size_ids else [])
                    
                    updated_variant_ids.append(int(variant_ids[i]))
                else:
                    # Create new
                    if i < len(variant_images):
                        variant_data['image'] = variant_images[i]
                    variant = ProductVariant.objects.create(**variant_data)
                    
                    # Add sizes to new variant
                    size_ids_key = f'variant_{i}_sizes[]'
                    size_ids = request.POST.getlist(size_ids_key)
                    if size_ids:
                        variant.sizes.set(size_ids)
                    
                    updated_variant_ids.append(variant.id)
        
        # Handle variant images (delete + add new)
        from products.models import VariantImage
        from django.db import models as db_models
        
        # Delete marked images
        delete_images = request.POST.getlist('delete_variant_images[]')
        if delete_images:
            for img_id in delete_images:
                if img_id:
                    try:
                        VariantImage.objects.filter(id=int(img_id)).delete()
                    except (ValueError, VariantImage.DoesNotExist):
                        pass
        
        # Add new images for each variant
        for idx, variant_id in enumerate(updated_variant_ids):
            new_images_key = f'variant_{idx}_new_images[]'
            new_images = request.FILES.getlist(new_images_key)
            
            if new_images:
                try:
                    variant = ProductVariant.objects.get(id=variant_id)
                    max_order = variant.images.aggregate(db_models.Max('order'))['order__max'] or -1
                    
                    for img_idx, img in enumerate(new_images):
                        VariantImage.objects.create(
                            variant=variant,
                            image=img,
                            order=max_order + img_idx + 1
                        )
                except ProductVariant.DoesNotExist:
                    pass
        
        # Delete variants not in the updated list
        ProductVariant.objects.filter(product=product).exclude(id__in=updated_variant_ids).delete()
        
        messages.success(request, 'تم تحديث المنتج بنجاح')
        return redirect('admin_app:admin_products')
    
    categories = Category.objects.all()
    variants = product.variants.all()
    product_images = product.additional_images.all()
    
    return render(request, 'admin/product_edit.html', {
        'product': product,
        'categories': categories,
        'colors': colors,
        'sizes': sizes,
        'variants': variants,  # Pass variants to template
        'product_images': product_images,  # Pass product images to template
    })


@staff_member_required
def admin_product_delete(request, product_id):
    """حذف منتج"""
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        product_name = product.name
        product.delete()
        messages.success(request, f'تم حذف المنتج {product_name}')
    return redirect('admin_app:admin_products')


@staff_member_required
def admin_orders(request):
    """إدارة الطلبات"""
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('search', '').strip()
    
    orders = Order.objects.all().select_related('user').prefetch_related('items__product').order_by('-created_at')
    
    # Apply search filter (order ID or customer name only)
    if search_query:
        orders = orders.filter(
            Q(id__icontains=search_query) |
            Q(user__username__icontains=search_query)
        ).distinct()
    
    # Apply status filter
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    return render(request, 'admin/orders.html', {
        'orders': orders,
        'status_filter': status_filter,
        'search_query': search_query,
    })



@staff_member_required
def admin_order_detail(request, order_id):
    """تفاصيل طلب في لوحة الإدارة"""
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES).keys():
            order.status = new_status
            order.save()
            messages.success(request, 'تم تحديث حالة الطلب')
    
    return render(request, 'admin/order_detail.html', {'order': order})


@staff_member_required
def admin_categories(request):
    """إدارة الأقسام"""
    categories = Category.objects.all().order_by('name')
    return render(request, 'admin/categories.html', {'categories': categories})


@staff_member_required
def admin_category_add(request):
    """إضافة قسم جديد"""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        image = request.FILES.get('image')
        
        try:
            category = Category.objects.create(
                name=name,
                description=description,
                image=image
            )
            messages.success(request, f'تم إضافة القسم "{category.name}" بنجاح')
            return redirect('admin_app:admin_categories')
        except Exception as e:
            messages.error(request, f'حدث خطأ: {str(e)}')
    
    return render(request, 'admin/category_add.html')


@staff_member_required
def admin_category_edit(request, category_id):
    """تعديل قسم"""
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        category.name = request.POST.get('name', category.name)
        category.description = request.POST.get('description', category.description)
        
        if 'image' in request.FILES:
            category.image = request.FILES['image']
        
        category.save()
        messages.success(request, 'تم تحديث القسم بنجاح')
        return redirect('admin_app:admin_categories')
    
    return render(request, 'admin/category_edit.html', {'category': category})


@staff_member_required
def admin_category_delete(request, category_id):
    """حذف قسم"""
    if request.method == 'POST':
        category = get_object_or_404(Category, id=category_id)
        category_name = category.name
        category.delete()
        messages.success(request, f'تم حذف القسم {category_name}')
    return redirect('admin_app:admin_categories')


@staff_member_required
def admin_pending_users(request):
    """عرض المستخدمين في انتظار الموافقة"""
    from accounts.models import CustomUser
    
    # Get all inactive users
    pending_users = CustomUser.objects.filter(is_active=False, is_staff=False).order_by('-date_joined')
    
    context = {
        'pending_users': pending_users,
        'pending_users_active': 'active',
    }
    return render(request, 'admin/pending_users.html', context)


@staff_member_required
def admin_all_users(request):
    """عرض جميع المستخدمين"""
    from accounts.models import CustomUser
    
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    users = CustomUser.objects.filter(is_staff=False).order_by('-date_joined')
    
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query)
        )
    
    if status_filter == 'active':
        users = users.filter(is_active=True)
    elif status_filter == 'inactive':
        users = users.filter(is_active=False)
    
    context = {
        'users': users,
        'search_query': search_query,
        'status_filter': status_filter,
        'all_users_active': 'active',
    }
    return render(request, 'admin/all_users.html', context)


@staff_member_required
def admin_approve_user(request, user_id):
    """الموافقة على مستخدم"""
    from accounts.models import CustomUser
    
    if request.method == 'POST':
        user = get_object_or_404(CustomUser, id=user_id, is_staff=False)
        user.is_active = True
        user.save()
        
        # Send activation email
        try:
            from django.core.mail import EmailMultiAlternatives
            from django.template.loader import render_to_string
            from django.utils.html import strip_tags
            from django.conf import settings
            
            subject = 'تم تفعيل حسابك - الوسام طلبات'
            login_url = request.build_absolute_uri('/accounts/login/')
            
            # Context for the email template
            context = {
                'username': user.username,
                'login_url': login_url,
            }
            
            # Render HTML content
            html_content = render_to_string('emails/activation_email.html', context)
            text_content = strip_tags(html_content)  # Fallback for plain text
            
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'info@elwsam.com')
            recipient_list = [user.email]
            
            # Create the email
            email = EmailMultiAlternatives(subject, text_content, from_email, recipient_list)
            email.attach_alternative(html_content, "text/html")
            email.send()
            
            messages.success(request, f'تم تفعيل حساب "{user.username}" وإرسال بريد إلكتروني للإشعار بنجاح')
            
        except Exception as e:
            messages.success(request, f'تم تفعيل حساب "{user.username}" (فشل إرسال البريد الإلكتروني: {str(e)})')
    
    return redirect('admin_app:pending_users')


@staff_member_required
def admin_reject_user(request, user_id):
    """رفض مستخدم وحذف حسابه"""
    from accounts.models import CustomUser
    
    if request.method == 'POST':
        user = get_object_or_404(CustomUser, id=user_id, is_staff=False)
        username = user.username
        user.delete()
        messages.success(request, f'تم رفض وحذف طلب انضمام "{username}"')
    
    return redirect('admin_app:pending_users')


@staff_member_required
def admin_toggle_user_status(request, user_id):
    """تبديل حالة تفعيل المستخدم (إيقاف/تفعيل)"""
    from accounts.models import CustomUser
    
    if request.method == 'POST':
        user = get_object_or_404(CustomUser, id=user_id, is_staff=False)
        
        # Toggle the active status
        user.is_active = not user.is_active
        user.save()
        
        if user.is_active:
            status_text = "تفعيل"
            # Send activation email
            try:
                from django.core.mail import EmailMultiAlternatives
                from django.template.loader import render_to_string
                from django.utils.html import strip_tags
                from django.conf import settings
                
                subject = 'تم تفعيل حسابك - الوسام طلبات'
                login_url = request.build_absolute_uri('/accounts/login/')
                
                context = {
                    'username': user.username,
                    'login_url': login_url,
                }
                
                html_content = render_to_string('emails/activation_email.html', context)
                text_content = strip_tags(html_content)
                
                from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'info@elwsam.com')
                recipient_list = [user.email]
                
                email = EmailMultiAlternatives(subject, text_content, from_email, recipient_list)
                email.attach_alternative(html_content, "text/html")
                email.send()
                
                messages.success(request, f'تم تفعيل حساب "{user.username}" وإرسال بريد إلكتروني للإشعار بنجاح')
            except Exception as e:
                messages.success(request, f'تم تفعيل حساب "{user.username}" (فشل إرسال البريد الإلكتروني: {str(e)})')
        else:
            status_text = "إيقاف"
            messages.success(request, f'تم {status_text} حساب المستخدم "{user.username}" بنجاح')
        
    return redirect('admin_app:all_users')
