import shutil
import tempfile
from io import BytesIO

from PIL import Image
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from products.models import Product, ProductSize, Size

from .models import CartItem


def _image_file():
    output = BytesIO()
    Image.new('RGB', (10, 10), 'blue').save(output, format='PNG')
    return SimpleUploadedFile('product.png', output.getvalue(), content_type='image/png')


class CartSizeQuantityTests(TestCase):
    def setUp(self):
        self.media_root = tempfile.mkdtemp()
        self.override = override_settings(MEDIA_ROOT=self.media_root)
        self.override.enable()
        self.addCleanup(self.override.disable)
        self.addCleanup(shutil.rmtree, self.media_root, True)

        self.user = get_user_model().objects.create_user(
            email='buyer@example.com', username='buyer', password='password',
            phone='01000000001', address='test', is_active=True,
        )
        self.client.force_login(self.user)

    def test_direct_size_uses_its_carton_quantity(self):
        product = Product.objects.create(name='منتج', pcs_carton=24, image=_image_file())
        size = Size.objects.create(name='كبير')
        ProductSize.objects.create(product=product, size=size, pcs_carton=48)

        response = self.client.post(reverse('cart:add_to_cart', args=[product.pk]), {
            'quantity': '2',
            'unit_type': 'carton',
            'size_name': size.name,
        })

        self.assertEqual(response.status_code, 302)
        item = CartItem.objects.get(product=product, size_name=size.name)
        self.assertEqual(item.quantity, 96)
        self.assertEqual(item.get_pcs_carton(), 48)
        self.assertEqual(item.get_quantity_in_cartons(), 2)
