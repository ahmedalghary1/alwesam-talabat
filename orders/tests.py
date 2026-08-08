import shutil
import tempfile
from io import BytesIO
from unittest.mock import patch

from PIL import Image
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.db.models.deletion import ProtectedError

from cart.models import Cart, CartItem
from products.models import Product, ProductSize, Size

from .models import OrderItem


def _image_file():
    output = BytesIO()
    Image.new('RGB', (10, 10), 'green').save(output, format='PNG')
    return SimpleUploadedFile('product.png', output.getvalue(), content_type='image/png')


class OrderSizeQuantityTests(TestCase):
    def setUp(self):
        self.media_root = tempfile.mkdtemp()
        self.override = override_settings(MEDIA_ROOT=self.media_root)
        self.override.enable()
        self.addCleanup(self.override.disable)
        self.addCleanup(shutil.rmtree, self.media_root, True)

        self.user = get_user_model().objects.create_user(
            email='order@example.com', username='order-buyer', password='password',
            phone='01000000002', address='test', is_active=True,
        )
        self.client.force_login(self.user)

    @patch('utils.email_tasks.send_order_confirmation_email_task.delay')
    def test_order_snapshots_direct_size_carton_quantity(self, send_email):
        product = Product.objects.create(name='منتج طلب', pcs_carton=24, image=_image_file())
        size = Size.objects.create(name='مقاس الطلب')
        ProductSize.objects.create(product=product, size=size, pcs_carton=60)
        cart, _ = Cart.objects.get_or_create(user=self.user)
        CartItem.objects.create(
            cart=cart,
            product=product,
            size=size,
            size_name=size.name,
            unit_type='carton',
            quantity=120,
        )

        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(reverse('orders:create_order'), {
                'phone_number': self.user.phone,
                'address': self.user.address,
            })

        self.assertEqual(response.status_code, 302)
        item = OrderItem.objects.get(product=product)
        self.assertEqual(item.pcs_carton, 60)
        self.assertEqual(item.get_quantity_in_cartons(), 2)
        send_email.assert_called_once_with(item.order_id, self.user.email)

    def test_product_delete_keeps_historical_order_items(self):
        product = Product.objects.create(name='منتج تاريخي', pcs_carton=24, image=_image_file())
        cart, _ = Cart.objects.get_or_create(user=self.user)
        CartItem.objects.create(
            cart=cart,
            product=product,
            unit_type='carton',
            quantity=24,
        )
        with patch('utils.email_tasks.send_order_confirmation_email_task.delay'):
            self.client.post(reverse('orders:create_order'), {
                'phone_number': self.user.phone,
                'address': self.user.address,
            })

        with self.assertRaises(ProtectedError):
            product.delete()

        self.assertEqual(OrderItem.objects.filter(product=product).count(), 1)

    @patch('utils.email_tasks.send_order_confirmation_email_task.delay')
    def test_order_without_email_does_not_schedule_confirmation(self, send_email):
        self.user.email = None
        self.user.save(update_fields=['email'])
        product = Product.objects.create(
            name='Order without email', pcs_carton=24, image=_image_file()
        )
        cart, _ = Cart.objects.get_or_create(user=self.user)
        CartItem.objects.create(
            cart=cart,
            product=product,
            unit_type='carton',
            quantity=24,
        )

        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(reverse('orders:create_order'), {
                'phone_number': self.user.phone,
                'address': self.user.address,
            })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(OrderItem.objects.filter(product=product).exists())
        send_email.assert_not_called()
