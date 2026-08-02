from django.db import models
from django.conf import settings
from products.models import Product, ProductVariant

User = settings.AUTH_USER_MODEL


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_item_count(self):
        return sum(item.quantity for item in self.items.all())

    def __str__(self):
        return f"Cart - {self.user.username}"

    class Meta:
        verbose_name = 'سلة التسوق'
        verbose_name_plural='سلات التسوق'

class CartItem(models.Model):
    """
    Individual item in shopping cart.
    
    Quantity is always stored in pieces internally, but can be displayed
    as cartons or pieces based on unit_type. This ensures accurate inventory tracking.
    """
    UNIT_TYPE_CHOICES = [
        ('piece', 'قطعة'),
        ('carton', 'كرتونة'),
    ]
    
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, blank=True)
    # Always stored in pieces for consistency
    quantity = models.PositiveIntegerField(default=1)
    # User's preferred display unit (converted to pieces internally)
    unit_type = models.CharField(max_length=10, choices=UNIT_TYPE_CHOICES, default='carton')
    size_name = models.CharField(max_length=100, blank=True, help_text="اسم الطول/المقاس المختار")

    class Meta:
        # Prevent duplicate items with same product/variant/unit/size
        unique_together = ['cart', 'product', 'variant', 'unit_type', 'size_name']
        verbose_name = 'تفاصيل السلة'
        verbose_name_plural='تفاصيل السلات '

        
    def get_pcs_carton(self):
        """Get the carton quantity for the selected variant and size."""
        if self.variant:
            if self.size_name:
                size_price = self.variant.size_prices.filter(
                    size__name=self.size_name
                ).values_list('pcs_carton', flat=True).first()
                if size_price is not None:
                    return size_price
            return self.variant.pcs_carton
        if self.size_name:
            size_price = self.product.size_prices.filter(
                size__name=self.size_name
            ).values_list('pcs_carton', flat=True).first()
            if size_price is not None:
                return size_price
        return self.product.pcs_carton
    
    def get_quantity_in_cartons(self):
        """Get quantity in cartons (for display)"""
        pcs_carton = self.get_pcs_carton()
        if pcs_carton > 0:
            return self.quantity / pcs_carton
        return 0
    
    def get_quantity_in_pieces(self):
        """Get quantity in pieces"""
        return self.quantity

    def get_display_name(self):
        """Display name with variant info"""
        if self.variant:
            return f"{self.product.name}"
        return self.product.name

    def __str__(self):
        unit = 'قطعة' if self.unit_type == 'piece' else 'كرتونة'
        if self.unit_type == 'piece':
            return f"{self.get_display_name()} x {self.quantity} قطعة"
        else:
            cartons = self.get_quantity_in_cartons()
            return f"{self.get_display_name()} x {cartons:.0f} كرتونة"
