import json
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST

from core.constants import MAX_QUANTITY_PER_ITEM
from products.models import Product

from .models import Cart, CartItem
from .services import InvalidProductSelection, resolve_product_selection

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

    # Get unit type from request
    unit_type = request.POST.get("unit_type", "carton")
    if unit_type not in {"carton", "piece"}:
        message = "وحدة الطلب غير صحيحة"
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"success": False, "message": message}, status=400)
        messages.error(request, message)
        return redirect("products:product_detail", slug=product.slug)

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

    try:
        selection = resolve_product_selection(
            product,
            variant_id=request.POST.get("variant_id"),
            size_id=request.POST.get("size_id"),
            size_name=request.POST.get("size_name", ""),
        )
    except InvalidProductSelection as exc:
        logger.warning(
            "Rejected invalid cart selection for product=%s variant=%r size=%r",
            product.pk,
            request.POST.get("variant_id"),
            request.POST.get("size_id"),
        )
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"success": False, "message": str(exc)}, status=400)
        messages.error(request, str(exc))
        return redirect("products:product_detail", slug=product.slug)

    variant = selection.variant
    size_name = selection.size.name if selection.size else ""
    pcs_carton = selection.pcs_carton

    # حساب الكمية بالقطع بناءً على الوحدة
    if unit_type == "carton":
        quantity_in_pieces = quantity * pcs_carton
    else:
        quantity_in_pieces = quantity

    cart, created = Cart.objects.get_or_create(user=request.user)

    # Get or create cart item with variant, unit_type, and size_name
    cart_item, item_created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        variant=variant,
        unit_type=unit_type,
        size_name=size_name,
        defaults={"quantity": quantity_in_pieces, "size": selection.size},
    )

    if not item_created:
        # Item already exists, increase quantity (in pieces)
        cart_item.quantity += quantity_in_pieces
        # Update size_name in case user selected a different size
        if size_name:
            cart_item.size_name = size_name
        cart_item.size = selection.size
        cart_item.save()

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
                "pcs_carton": pcs_carton,
                "size_id": selection.size.pk if selection.size else None,
                "size_name": size_name,
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
            unit_type = item.get("unit_type", "carton")

            try:
                product = Product.objects.get(id=product_id, is_available=True)
                if unit_type not in {"carton", "piece"}:
                    raise ValueError("Invalid unit type")

                selection = resolve_product_selection(
                    product,
                    variant_id=item.get("variant_id"),
                    size_id=item.get("size_id"),
                    size_name=item.get("size_name", ""),
                )

                # New local carts keep the quantity selected by the user. For
                # legacy carts, recover it from the piece total and old carton
                # size to avoid multiplying an already-converted value twice.
                unit_quantity = item.get("unit_quantity")
                if unit_quantity is None:
                    stored_quantity = int(item.get("quantity", 0))
                    if unit_type == "carton":
                        old_pcs_carton = int(item.get("pcs_carton") or selection.pcs_carton)
                        if old_pcs_carton < 1 or stored_quantity % old_pcs_carton:
                            raise ValueError("Invalid legacy carton quantity")
                        unit_quantity = stored_quantity // old_pcs_carton
                    else:
                        unit_quantity = stored_quantity
                unit_quantity = int(unit_quantity)
                if not 1 <= unit_quantity <= MAX_QUANTITY_PER_ITEM:
                    raise ValueError("Invalid quantity")

                if unit_type == "carton":
                    quantity_in_pieces = unit_quantity * selection.pcs_carton
                else:
                    quantity_in_pieces = unit_quantity

                size_name = selection.size.name if selection.size else ""

                cart_item, created = CartItem.objects.get_or_create(
                    cart=cart,
                    product=product,
                    variant=selection.variant,
                    unit_type=unit_type,
                    size_name=size_name,
                    defaults={"quantity": quantity_in_pieces, "size": selection.size},
                )

                if not created:
                    cart_item.quantity += quantity_in_pieces
                    cart_item.size = selection.size
                    cart_item.save()

                synced_count += 1
            except (Product.DoesNotExist, InvalidProductSelection, TypeError, ValueError) as exc:
                logger.warning(
                    "Skipping invalid local cart item for product=%s (%s)",
                    product_id,
                    type(exc).__name__,
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
