import shutil
import tempfile
from io import BytesIO

from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Product, ProductSize, Size


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
        self.assertContains(response, "selectDirectSize('كبير', 48, this)")
