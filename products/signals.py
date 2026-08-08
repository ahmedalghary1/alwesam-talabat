from django.db import transaction
from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import (
    Category, Product, ProductImages, ProductSizeImage, ProductVariant,
    VariantImage, VariantSizeImage,
)


@receiver(post_delete, sender=Category)
@receiver(post_delete, sender=Product)
@receiver(post_delete, sender=ProductImages)
@receiver(post_delete, sender=ProductVariant)
@receiver(post_delete, sender=VariantImage)
@receiver(post_delete, sender=ProductSizeImage)
@receiver(post_delete, sender=VariantSizeImage)
def delete_model_image_after_commit(sender, instance, **kwargs):
    """Remove an image file only after its database deletion succeeds."""
    image = getattr(instance, 'image', None)
    if image and image.name:
        storage = image.storage
        name = image.name
        transaction.on_commit(lambda: storage.delete(name))
