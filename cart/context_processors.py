"""
Context processors for the cart app
"""
from .models import Cart


def cart_count(request):
    """
    Context processor to add cart count to all templates
    """
    count = 0
    
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            # Use get_item_count() which sums all quantities (in pieces)
            count = cart.get_item_count()
        except Cart.DoesNotExist:
            count = 0
    else:
        # For non-authenticated users, get from localStorage (handled in frontend)
        count = 0
    
    return {'cart_count': count}
