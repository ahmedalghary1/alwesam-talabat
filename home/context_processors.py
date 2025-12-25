from cart.models import Cart


def cart_context(request):
    """Add cart information to template context."""
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            cart_detail_data = cart.items.all()
        except Cart.DoesNotExist:
            cart_detail_data = []
    else:
        cart_detail_data = []
    
    return {
        'cart_count': cart_detail_data
    }
