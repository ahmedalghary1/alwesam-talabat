import shutil
import tempfile
from io import BytesIO

from PIL import Image
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, SimpleTestCase, TestCase, override_settings

from products.models import (
    Product, ProductSize, ProductVariant, Size, VariantImage, VariantSize,
)

from .admin_views import _valid_model_ids, _variant_sizes_from_post


class ValidModelIdsTests(SimpleTestCase):
    def test_ignores_blank_and_invalid_values(self):
        self.assertEqual(
            _valid_model_ids(['', '  ', 'invalid', None, '7']),
            [7],
        )

    def test_accepts_only_positive_integer_ids(self):
        self.assertEqual(
            _valid_model_ids(['1', '0', '-2', '3']),
            [1, 3],
        )

    def test_variant_sizes_keep_the_quantity_for_each_checked_size(self):
        request = RequestFactory().post('/', {
            'variant_7_size_ids[]': ['2', '9'],
            'variant_7_size_pcs_2': '12',
            'variant_7_size_pcs_9': '30',
        })

        self.assertEqual(_variant_sizes_from_post(request, '7'), [(2, 12), (9, 30)])


def _image_file(name='test.png', color='red'):
    output = BytesIO()
    Image.new('RGB', (20, 20), color).save(output, format='PNG')
    return SimpleUploadedFile(name, output.getvalue(), content_type='image/png')


class ProductAdminFlowTests(TestCase):
    def setUp(self):
        self.media_root = tempfile.mkdtemp()
        self.override = override_settings(MEDIA_ROOT=self.media_root)
        self.override.enable()
        self.addCleanup(self.override.disable)
        self.addCleanup(shutil.rmtree, self.media_root, True)

        user_model = get_user_model()
        self.staff = user_model.objects.create_user(
            email='admin@example.com', username='admin', password='password',
            phone='01000000000', address='test', is_staff=True, is_active=True,
        )
        self.client.force_login(self.staff)

    def test_edit_uses_stable_variant_key_for_availability_and_images(self):
        product = Product.objects.create(name='منتج', image=_image_file())
        removed = ProductVariant.objects.create(product=product, name='قديم')
        kept = ProductVariant.objects.create(product=product, name='مستمر', is_available=False)

        response = self.client.post(
            f'/admin-panel/products/{product.pk}/edit/',
            {
                'name': product.name,
                'pcs_carton': '24',
                'order': '0',
                'is_available': 'on',
                'variant_form_key[]': ['7'],
                'variant_id[]': [str(kept.pk)],
                'variant_name[]': ['مستمر'],
                'variant_code[]': [''],
                'variant_pcs_carton[]': ['24'],
                'variant_available[]': ['7'],
                'variant_color[]': [''],
                'variant_length_label[]': [''],
                'variant_7_new_images[]': _image_file('variant.png', 'blue'),
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(ProductVariant.objects.filter(pk=removed.pk).exists())
        kept.refresh_from_db()
        self.assertTrue(kept.is_available)
        self.assertEqual(VariantImage.objects.filter(variant=kept).count(), 1)

    def test_add_product_saves_the_quantity_for_each_variant_size(self):
        first_size = Size.objects.create(name='مقاس أول')
        second_size = Size.objects.create(name='مقاس ثان')

        response = self.client.post(
            '/admin-panel/products/add/',
            {
                'name': 'منتج بكميات مقاسات',
                'image': _image_file('sized-product.png'),
                'pcs_carton': '24',
                'is_available': 'on',
                'variant_form_key[]': ['0'],
                'variant_name[]': ['النمط الأول'],
                'variant_code[]': [''],
                'variant_pcs_carton[]': ['30'],
                'variant_available[]': ['0'],
                'variant_color[]': [''],
                'variant_length_label[]': [''],
                'variant_0_size_ids[]': [str(first_size.pk), str(second_size.pk)],
                'variant_0_size_pcs[]': ['12', '60'],
            },
        )

        self.assertEqual(response.status_code, 302)
        variant = ProductVariant.objects.get(product__name='منتج بكميات مقاسات')
        self.assertTrue(VariantSize.objects.filter(
            variant=variant, size=first_size, pcs_carton=12,
        ).exists())
        self.assertTrue(VariantSize.objects.filter(
            variant=variant, size=second_size, pcs_carton=60,
        ).exists())

    def test_repeated_arabic_product_names_get_unique_slugs(self):
        first = Product.objects.create(name='منتج مكرر', image=_image_file('one.png'))
        second = Product.objects.create(name='منتج مكرر', image=_image_file('two.png'))

        self.assertEqual(first.slug, 'منتج-مكرر')
        self.assertEqual(second.slug, 'منتج-مكرر-2')
        self.assertTrue(first.image.name.endswith('.webp'))

    def test_edit_keeps_a_new_direct_size(self):
        product = Product.objects.create(name='منتج مقاسات', image=_image_file())
        size = Size.objects.create(name='كبير')

        response = self.client.post(
            f'/admin-panel/products/{product.pk}/edit/',
            {
                'name': product.name,
                'pcs_carton': '24',
                'order': '0',
                'new_product_size_id[]': [str(size.pk)],
                'new_product_size_pcs[]': ['48'],
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(ProductSize.objects.filter(
            product=product, size=size, pcs_carton=48,
        ).exists())

    def test_edit_page_renders_product_data(self):
        product = Product.objects.create(name='منتج "آمن"', image=_image_file())
        ProductVariant.objects.create(product=product, name='<نمط>')

        response = self.client.get(f'/admin-panel/products/{product.pk}/edit/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="variants-data"')
        self.assertNotContains(response, '<نمط>')

# Create your tests here.
