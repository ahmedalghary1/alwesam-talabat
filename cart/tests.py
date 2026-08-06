import json
import shutil
import tempfile
from io import BytesIO

from PIL import Image
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIRequestFactory, force_authenticate

from api.v1.views.cart import CartViewSet
from products.models import Product, ProductSize, ProductVariant, Size, VariantSize

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
            'size_id': size.pk,
            'size_name': size.name,
        })

        self.assertEqual(response.status_code, 302)
        item = CartItem.objects.get(product=product, size_name=size.name)
        self.assertEqual(item.size, size)
        self.assertEqual(item.quantity, 96)
        self.assertEqual(item.get_pcs_carton(), 48)
        self.assertEqual(item.get_quantity_in_cartons(), 2)

    def test_variant_size_uses_its_carton_quantity(self):
        product = Product.objects.create(name='منتج بنمط', pcs_carton=24, image=_image_file())
        size = Size.objects.create(name='وسط')
        variant = ProductVariant.objects.create(
            product=product, name='النمط الأول', pcs_carton=30, is_available=True
        )
        VariantSize.objects.create(variant=variant, size=size, pcs_carton=72)

        response = self.client.post(reverse('cart:add_to_cart', args=[product.pk]), {
            'quantity': '2',
            'unit_type': 'carton',
            'variant_id': variant.pk,
            'size_id': size.pk,
        })

        self.assertEqual(response.status_code, 302)
        item = CartItem.objects.get(product=product, variant=variant, size_name=size.name)
        self.assertEqual(item.size, size)
        self.assertEqual(item.quantity, 144)
        self.assertEqual(item.get_quantity_in_cartons(), 2)

    def test_size_is_required_when_variant_has_sizes(self):
        product = Product.objects.create(name='منتج يحتاج مقاس', image=_image_file())
        size = Size.objects.create(name='كبير')
        variant = ProductVariant.objects.create(product=product, name='نمط', is_available=True)
        VariantSize.objects.create(variant=variant, size=size, pcs_carton=48)

        response = self.client.post(
            reverse('cart:add_to_cart', args=[product.pk]),
            {'quantity': 1, 'unit_type': 'carton', 'variant_id': variant.pk},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(CartItem.objects.filter(product=product).exists())

    def test_rejects_size_that_belongs_to_another_variant(self):
        product = Product.objects.create(name='منتج', image=_image_file())
        first_variant = ProductVariant.objects.create(
            product=product, name='نمط أول', is_available=True
        )
        second_variant = ProductVariant.objects.create(
            product=product, name='نمط ثان', is_available=True
        )
        first_size = Size.objects.create(name='صغير')
        second_size = Size.objects.create(name='كبير')
        VariantSize.objects.create(variant=first_variant, size=first_size, pcs_carton=12)
        VariantSize.objects.create(variant=second_variant, size=second_size, pcs_carton=60)

        response = self.client.post(
            reverse('cart:add_to_cart', args=[product.pk]),
            {
                'quantity': 1,
                'unit_type': 'carton',
                'variant_id': first_variant.pk,
                'size_id': second_size.pk,
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(CartItem.objects.filter(product=product).exists())

    def test_local_cart_sync_does_not_convert_legacy_piece_total_twice(self):
        product = Product.objects.create(name='منتج محلي', image=_image_file())
        size = Size.objects.create(name='مقاس محلي')
        ProductSize.objects.create(product=product, size=size, pcs_carton=48)

        response = self.client.post(
            reverse('cart:sync_cart'),
            data=json.dumps({
                'cart_items': [{
                    'product_id': product.pk,
                    'quantity': 96,
                    'pcs_carton': 48,
                    'unit_type': 'carton',
                    'size_id': size.pk,
                    'size_name': size.name,
                }],
            }),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        item = CartItem.objects.get(product=product, size_name=size.name)
        self.assertEqual(item.quantity, 96)
        self.assertEqual(item.get_quantity_in_cartons(), 2)

    def test_api_add_uses_selected_size_carton_quantity(self):
        product = Product.objects.create(name='منتج API', image=_image_file())
        size = Size.objects.create(name='مقاس API')
        ProductSize.objects.create(product=product, size=size, pcs_carton=54)
        request = APIRequestFactory().post('/api/v1/cart/add_item/', {
            'product_id': product.pk,
            'quantity': 2,
            'unit_type': 'carton',
            'size_id': size.pk,
        }, format='json')
        force_authenticate(request, user=self.user)

        response = CartViewSet.as_view({'post': 'add_item'})(request)

        self.assertEqual(response.status_code, 201)
        item = CartItem.objects.get(product=product, size=size)
        self.assertEqual(item.quantity, 108)

    def test_api_update_converts_cartons_to_pieces(self):
        product = Product.objects.create(name='منتج تحديث API', image=_image_file(), pcs_carton=24)
        item = CartItem.objects.create(
            cart=self.user.cart,
            product=product,
            unit_type='carton',
            quantity=48,
        )
        request = APIRequestFactory().post('/api/v1/cart/update_item/', {
            'item_id': item.pk,
            'quantity': 3,
        }, format='json')
        force_authenticate(request, user=self.user)

        response = CartViewSet.as_view({'post': 'update_item'})(request)

        self.assertEqual(response.status_code, 200)
        item.refresh_from_db()
        self.assertEqual(item.quantity, 72)
        self.assertEqual(item.get_quantity_in_cartons(), 3)

    def test_carton_snapshot_survives_product_changes(self):
        product = Product.objects.create(name='منتج لقطة', image=_image_file(), pcs_carton=24)
        item = CartItem.objects.create(
            cart=self.user.cart,
            product=product,
            unit_type='carton',
            quantity=48,
        )

        product.pcs_carton = 30
        product.save(update_fields=['pcs_carton'])
        item.refresh_from_db()

        self.assertEqual(item.get_pcs_carton(), 24)
        self.assertEqual(item.get_quantity_in_cartons(), 2)

    def test_repeated_add_cannot_exceed_quantity_limit(self):
        product = Product.objects.create(name='منتج حد الكمية', image=_image_file())
        first = self.client.post(reverse('cart:add_to_cart', args=[product.pk]), {
            'quantity': 60,
            'unit_type': 'piece',
        })
        second = self.client.post(
            reverse('cart:add_to_cart', args=[product.pk]),
            {'quantity': 50, 'unit_type': 'piece'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )

        self.assertEqual(first.status_code, 302)
        self.assertEqual(second.status_code, 400)
        self.assertEqual(CartItem.objects.get(product=product).quantity, 60)
