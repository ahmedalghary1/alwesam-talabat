from django.db import models
from django.conf import settings
from products.models import Product, ProductVariant

User = settings.AUTH_USER_MODEL


class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'قيد الانتظار'),
        ('confirmed', 'تم التأكيد'),
        ('shipped', 'تم الشحن'),
        ('delivered', 'تم التسليم'),
        ('cancelled', 'تم الإلغاء'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    phone_number = models.CharField(max_length=20)
    address = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"

    class Meta:
        ordering = ['-created_at']


class OrderItem(models.Model):
    UNIT_TYPE_CHOICES = [
        ('piece', 'قطعة'),
        ('carton', 'كرتونة'),
    ]
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)  # Always stored in pieces
    unit_type = models.CharField(max_length=10, choices=UNIT_TYPE_CHOICES, default='carton')
    
    # Preserve variant information at order time
    variant_info = models.CharField(max_length=200, blank=True, 
                                    help_text="معلومات النمط وقت الطلب")
    variant_pcs_carton = models.PositiveIntegerField(null=True, blank=True,
                                                     help_text="عدد القطع في الكرتونة وقت الطلب")

    def save(self, *args, **kwargs):
        # Automatically save variant info when order is created
        if self.variant and not self.variant_info:
            self.variant_info = f"{self.variant.get_variant_type_display()}: {self.variant.variant_value}"
        if self.variant and not self.variant_pcs_carton:
            self.variant_pcs_carton = self.variant.pcs_carton
        super().save(*args, **kwargs)

    def get_pcs_carton(self):
        """Get pcs_carton from preserved value, variant, or product"""
        if self.variant_pcs_carton:
            return self.variant_pcs_carton
        if self.variant:
            return self.variant.pcs_carton
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
    
    def get_total_pieces(self):
        """Calculate total pieces in this order item (same as quantity)"""
        return self.quantity

    def get_display_name(self):
        """Display name with variant"""
        if self.variant_info:
            return f"{self.product.name} ({self.variant_info})"
        return self.product.name

    def __str__(self):
        unit = 'قطعة' if self.unit_type == 'piece' else 'كرتونة'
        if self.unit_type == 'piece':
            return f"{self.get_display_name()} x {self.quantity} قطعة"
        else:
            cartons = self.get_quantity_in_cartons()
            return f"{self.get_display_name()} x {cartons:.0f} كرتونة"
