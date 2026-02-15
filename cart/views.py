import json
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST

from core.constants import MAX_QUANTITY_PER_ITEM
from products.models import Product, ProductVariant

from .models import Cart, CartItem

logger = logging.getLogger(__name__)


def cart_view(request):
    """
    Display the cart
    """
    cart = None
    cart_items = []
    total_cartons = 0
    total_pieces = 0

    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_items = cart.items.select_related("product", "variant").all()

        # Calculate totals
        for item in cart_items:
            if item.unit_type == "carton":
                total_cartons += item.get_quantity_in_cartons()
            total_pieces += item.quantity  # Always count pieces

    return render(
        request,
        "cart/cart.html",
        {
            "cart": cart,
            "cart_items": cart_items,
            "total_cartons": int(total_cartons),
            "total_pieces": total_pieces,
        },
    )


@ensure_csrf_cookie
def add_to_cart(request, product_id):
    """
    Add product to cart - for authenticated users only
    """
    # Check if user is authenticated
    if not request.user.is_authenticated:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse(
                {
                    "success": False,
                    "message": "يجب تسجيل الدخول أولاً",
                    "requires_login": True,
                },
                status=401,
            )
        return redirect("accounts:login")

    product = get_object_or_404(Product, id=product_id)

    # Check if product is available
    if not product.is_available:
        logger.warning(f"Attempt to add unavailable product {product_id} to cart")
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse(
                {"success": False, "message": "عذراً، هذا المنتج غير متوفر حالياً"},
                status=400,
            )
        messages.error(request, "عذراً، هذا المنتج غير متوفر حالياً")
        return redirect("products:product_detail", slug=product.slug)

    # Get unit type from request (NEW)
    unit_type = request.POST.get("unit_type", "carton")

    # Validate quantity
    try:
        quantity = int(request.POST.get("quantity", 1))
        if quantity <= 0:
            raise ValueError("الكمية يجب أن تكون أكبر من صفر")
        if quantity > MAX_QUANTITY_PER_ITEM:
            raise ValueError(f"الكمية القصوى هي {MAX_QUANTITY_PER_ITEM}")
    except (ValueError, TypeError) as e:
        logger.warning(f"Invalid quantity in add_to_cart: {e}")
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse(
                {"success": False, "message": f"كمية غير صحيحة: {str(e)}"}, status=400
            )
        messages.error(request, f"كمية غير صحيحة: {str(e)}")
        return redirect(request.META.get("HTTP_REFERER", "products:all_categories"))

    variant_id = request.POST.get("variant_id")  # NEW: variant support
    size_name = request.POST.get("size_name", "")  # NEW: get selected size name

    logger.info(f"=== add_to_cart Debug ===")
    logger.info(f"POST data: {dict(request.POST)}")
    logger.info(f"variant_id: {variant_id}")
    logger.info(f"size_name received: '{size_name}'")
    logger.info(f"size_name type: {type(size_name)}")
    logger.info(f"size_name length: {len(size_name) if size_name else 0}")

    # Calculate quantity in pieces based on unit type (NEW)
    quantity_in_pieces = quantity
    if unit_type == "carton":
        # Get variant if exists
        variant = None
        if variant_id:
            try:
                variant = ProductVariant.objects.get(id=variant_id)

                # Check if variant is available
                if not variant.is_available:
                    logger.warning(
                        f"Attempt to add unavailable variant {variant_id} to cart"
                    )
                    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                        return JsonResponse(
                            {
                                "success": False,
                                "message": "عذراً، هذا النمط غير متوفر حالياً",
                            },
                            status=400,
                        )
                    messages.error(request, "عذراً، هذا النمط غير متوفر حالياً")
                    return redirect("products:product_detail", slug=product.slug)

                pcs_carton = variant.pcs_carton
            except ProductVariant.DoesNotExist:
                pcs_carton = product.pcs_carton
        else:
            pcs_carton = product.pcs_carton

        quantity_in_pieces = quantity * pcs_carton

    cart, created = Cart.objects.get_or_create(user=request.user)

    logger.info(f"Before get_or_create - size_name: '{size_name}'")

    # Get or create cart item with variant, unit_type, and size_name (UPDATED)
    cart_item, item_created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        variant_id=variant_id if variant_id else None,
        unit_type=unit_type,  # Include unit_type in lookup
        size_name=size_name,  # NEW: Include size_name in lookup to treat different sizes as separate items
        defaults={"quantity": quantity_in_pieces},
    )

    logger.info(
        f"After get_or_create - item_created: {item_created}, cart_item.size_name: '{cart_item.size_name}'"
    )

    if not item_created:
        # Item already exists, increase quantity (in pieces)
        cart_item.quantity += quantity_in_pieces
        # Update size_name in case user selected a different size
        if size_name:
            cart_item.size_name = size_name
        cart_item.save()
        logger.info(f"CartItem updated - size_name: '{cart_item.size_name}'")
    else:
        logger.info(f"CartItem created - size_name: '{cart_item.size_name}'")

    message = f"تم إضافة {product.name} إلى السلة"
    if cart_item.variant:
        message = f"تم إضافة {cart_item.get_display_name()} إلى السلة"

    # AJAX response
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse(
            {
                "success": True,
                "message": message,
                "cart_count": cart.get_item_count(),
                "product_id": product.id,
                "product_name": product.name,
                "quantity": cart_item.quantity,
            }
        )

    messages.success(request, message)
    return redirect("products:product_detail", slug=product.slug)


@login_required
def remove_from_cart(request, item_id):
    """
    Remove product from cart
    """
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    product_name = (
        cart_item.get_display_name()
        if hasattr(cart_item, "get_display_name")
        else cart_item.product.name
    )
    cart_item.delete()

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        cart = Cart.objects.get(user=request.user)
        return JsonResponse(
            {
                "success": True,
                "message": f'✓ تم حذف "{product_name}" من السلة بنجاح',
                "cart_count": cart.get_item_count(),
            }
        )
    return redirect("cart:cart_view")


@login_required
def update_cart_item(request, item_id):
    """
    Update product quantity in cart
    """
    if request.method == "POST":
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)

        # Get the new quantity from the request
        quantity = int(request.POST.get("quantity", 1))

        # Important: Keep the existing unit_type, convert quantity based on it
        if cart_item.unit_type == "carton":
            # User is updating carton quantity, convert to pieces
            pcs_carton = cart_item.get_pcs_carton()
            quantity_in_pieces = quantity * pcs_carton
        else:
            # User is updating piece quantity directly
            quantity_in_pieces = quantity

        if quantity_in_pieces > 0:
            cart_item.quantity = quantity_in_pieces
            cart_item.save()
        else:
            cart_item.delete()

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            cart = Cart.objects.get(user=request.user)
            return JsonResponse({"success": True, "cart_count": cart.get_item_count()})
    return redirect("cart:cart_view")


@require_POST
def sync_cart_from_local(request):
    """
    Synchronize cart from localStorage
    """
    if not request.user.is_authenticated:
        return JsonResponse(
            {"success": False, "message": "يجب تسجيل الدخول أولاً"}, status=401
        )

    try:
        data = json.loads(request.body)
        cart_items = data.get("cart_items", [])

        cart, created = Cart.objects.get_or_create(user=request.user)

        synced_count = 0
        for item in cart_items:
            product_id = item.get("product_id")
            quantity = item.get("quantity", 1)
            variant_id = item.get(
                "variant_id"
            )  # Assuming variant_id might be in local storage
            unit_type = item.get(
                "unit_type", "carton"
            )  # Assuming unit_type might be in local storage
            size_name = item.get(
                "size_name", ""
            )  # NEW: Get size_name from localStorage

            try:
                product = Product.objects.get(id=product_id)

                # Check if product is available
                if not product.is_available:
                    logger.warning(
                        f"Product {product.id} is not available, skipping sync."
                    )
                    continue

                variant = None
                if variant_id:
                    try:
                        variant = ProductVariant.objects.get(
                            id=variant_id, product=product
                        )
                        if not variant.is_available:
                            logger.warning(
                                f"Variant {variant.id} for product {product.id} is not available, skipping sync."
                            )
                            continue
                    except ProductVariant.DoesNotExist:
                        logger.warning(
                            f"Variant {variant_id} for product {product.id} not found, skipping sync."
                        )
                        continue

                # Calculate quantity in pieces based on unit type
                quantity_in_pieces = quantity
                if unit_type == "carton":
                    if variant:
                        pcs_carton = variant.pcs_carton
                    else:
                        pcs_carton = product.pcs_carton
                    quantity_in_pieces = quantity * pcs_carton

                cart_item, created = CartItem.objects.get_or_create(
                    cart=cart,
                    product=product,
                    variant=variant,  # Use the variant object
                    unit_type=unit_type,  # Include unit_type in lookup
                    size_name=size_name,  # NEW: Include size_name in lookup
                    defaults={"quantity": quantity_in_pieces},
                )

                if not created:
                    cart_item.quantity += quantity_in_pieces  # Add in pieces
                    cart_item.save()

                synced_count += 1
            except Product.DoesNotExist:
                logger.warning(
                    f"Product {product_id} not found during cart sync, skipping."
                )
                continue

        return JsonResponse(
            {
                "success": True,
                "message": f"تم مزامنة {synced_count} منتج",
                "cart_count": cart.get_item_count(),
            }
        )
    except Exception as e:
        return JsonResponse(
            {"success": False, "message": f"حدث خطأ: {str(e)}"}, status=400
        )


@login_required
def checkout(request):
    """
    Checkout page
    """
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = cart.items.all()

    if not cart_items:
        return redirect("cart:cart_view")

    # Calculate total quantity
    total_quantity = sum(item.quantity for item in cart_items)

    return render(
        request,
        "cart/checkout.html",
        {
            "cart": cart,
            "cart_items": cart_items,
            "total_quantity": total_quantity,
        },
    )
