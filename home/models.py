from django.db import models
from django.db import transaction

from utils.image_utils import ImageCompressionMixin


class HomeSlide(ImageCompressionMixin, models.Model):
    title = models.CharField(max_length=150, verbose_name='اسم السلايد')
    image_width = models.PositiveIntegerField(default=0, editable=False)
    image_height = models.PositiveIntegerField(default=0, editable=False)
    image = models.ImageField(
        upload_to='home/slides/',
        width_field='image_width',
        height_field='image_height',
        verbose_name='الصورة',
    )
    alt_text = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='النص البديل للصورة',
    )
    order = models.PositiveIntegerField(default=0, db_index=True, verbose_name='الترتيب')
    is_active = models.BooleanField(default=True, db_index=True, verbose_name='نشط')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'سلايد الصفحة الرئيسية'
        verbose_name_plural = 'سلايدر الصفحة الرئيسية'

    def save(self, *args, **kwargs):
        update_fields = kwargs.get('update_fields')
        if update_fields and 'image' not in update_fields:
            super().save(*args, **kwargs)
        else:
            self.save_with_compression(
                image_field_name='image',
                compression_options={'max_width': 2048, 'max_height': 886},
                *args,
                **kwargs,
            )

    def delete(self, *args, **kwargs):
        storage = self.image.storage
        image_name = self.image.name
        result = super().delete(*args, **kwargs)
        if image_name:
            transaction.on_commit(lambda: storage.delete(image_name))
        return result

    def __str__(self):
        return self.title
