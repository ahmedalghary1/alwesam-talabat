from django.db import models
from django.conf import settings
from products.models import Product, ProductVariant

User = settings.AUTH_USER_MODEL


class Order(models.Model):
    """
    Customer order representing a purchase transaction.
    
    Tracks order status from pending to delivered/cancelled.
    Contains user contact info and order metadata.
    """
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

    def get_total_pieces(self):
        """Calculate total pieces across all order items"""
        return sum(item.quantity for item in self.items.all())

    class Meta:
        ordering = ['-created_at']
        verbose_name='الطلب'
        verbose_name_plural='الطلبات'

class OrderItem(models.Model):
    UNIT_TYPE_CHOICES = [
        ('piece', 'قطعة'),
        ('carton', 'كرتونة'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    # Keep historical order lines intact. Products referenced by an order must
    # be archived (is_available=False) instead of being physically deleted.
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)  # مخزنة بالقطع دائماً
    unit_type = models.CharField(max_length=10, choices=UNIT_TYPE_CHOICES, default='carton')

    # بيانات محفوظة وقت الطلب
    color_name = models.CharField(max_length=100, blank=True)
    size_name = models.CharField(max_length=100, blank=True)
    pcs_carton = models.PositiveIntegerField(default=24, verbose_name="عدد القطع في الكرتونة وقت الطلب")

    class Meta:
        verbose_name = 'تفاصيل الطلب'
        verbose_name_plural = 'تفاصيل الطلبات'

    def get_quantity_in_cartons(self):
        if self.unit_type == 'carton' and self.pcs_carton:
            return self.quantity // self.pcs_carton
        return 0

    def get_display_name(self):
        parts = [self.product.name]
        if self.color_name:
            parts.append(f"لون: {self.color_name}")
        if self.size_name:
            parts.append(f"مقاس: {self.size_name}")
        if self.variant and not (self.color_name or self.size_name):
            parts.append(self.variant.name)
        return " - ".join(parts)

    def __str__(self):
        if self.unit_type == 'piece':
            return f"{self.get_display_name()} x {self.quantity} قطعة"
        else:
            cartons = self.get_quantity_in_cartons()
            return f"{self.get_display_name()} x {cartons} كرتونة ({self.quantity} قطعة)"
