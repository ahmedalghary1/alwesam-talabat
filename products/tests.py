import shutil
import tempfile
from io import BytesIO

from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Product, ProductSize, ProductVariant, Size, VariantSize


def _image_file():
    output = BytesIO()
    Image.new('RGB', (10, 10), 'red').save(output, format='PNG')
    return SimpleUploadedFile('product.png', output.getvalue(), content_type='image/png')


class ProductDetailSizeQuantityTests(TestCase):
    def setUp(self):
        self.media_root = tempfile.mkdtemp()
        self.override = override_settings(MEDIA_ROOT=self.media_root)
        self.override.enable()
        self.addCleanup(self.override.disable)
        self.addCleanup(shutil.rmtree, self.media_root, True)

    def test_direct_size_includes_its_carton_quantity_in_page(self):
        product = Product.objects.create(name='منتج', pcs_carton=24, image=_image_file())
        size = Size.objects.create(name='كبير')
        ProductSize.objects.create(product=product, size=size, pcs_carton=48)

        response = self.client.get(reverse('products:product_detail', args=[product.slug]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-pcs-carton="48"')
        self.assertEqual(
            response.context['product_page_data']['directSizePrices'][0]['pcsCarton'],
            48,
        )
        self.assertContains(response, 'id="product-page-data"')

    def test_variant_size_quantity_is_sent_from_database(self):
        product = Product.objects.create(name='منتج بنمط', pcs_carton=24, image=_image_file())
        size = Size.objects.create(name='وسط')
        variant = ProductVariant.objects.create(product=product, name='نمط', pcs_carton=30)
        VariantSize.objects.create(variant=variant, size=size, pcs_carton=72)

        response = self.client.get(reverse('products:product_detail', args=[product.slug]))

        size_data = response.context['product_page_data']['variants'][0]['sizePrices'][0]
        self.assertEqual(size_data['sizeId'], size.pk)
        self.assertEqual(size_data['pcsCarton'], 72)
