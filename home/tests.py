import shutil
import tempfile
from io import BytesIO

from PIL import Image
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, SimpleTestCase, TestCase, override_settings
from django.urls import reverse
from openpyxl import load_workbook

from orders.models import Order
from products.models import (
    Product, ProductSize, ProductVariant, Size, VariantImage, VariantSize,
)
from support.models import CustomerMessage

from .admin_views import _excel_safe_text, _valid_model_ids, _variant_sizes_from_post


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

    def test_excel_text_cannot_be_interpreted_as_a_formula(self):
        self.assertEqual(_excel_safe_text('=2+2'), "'=2+2")
        self.assertEqual(_excel_safe_text('+201000000000'), "'+201000000000")
        self.assertEqual(_excel_safe_text('بيانات عربية'), 'بيانات عربية')


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


class UserExcelExportTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.staff = user_model.objects.create_user(
            email='admin@example.com',
            username='admin',
            password='password',
            phone='01000000000',
            address='القاهرة',
            is_staff=True,
            is_active=True,
        )
        self.user = user_model.objects.create_user(
            email='customer@example.com',
            username='عميل-الوسام',
            password='customer-password',
            phone='01012345678',
            address='القاهرة، مدينة نصر',
            first_name='محمد',
            last_name='علي',
            is_active=True,
        )
        self.user.profile.bio = 'عميل جملة'
        self.user.profile.save()
        Order.objects.create(
            user=self.user,
            phone_number=self.user.phone,
            address=self.user.address,
        )
        CustomerMessage.objects.create(user=self.user, message='رسالة اختبار')
        self.export_url = reverse('admin_app:export_users_excel')

    def test_only_staff_can_export_users(self):
        response = self.client.get(self.export_url)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/login/', response.url)

    def test_users_page_shows_the_excel_export_button(self):
        self.client.force_login(self.staff)

        response = self.client.get(reverse('admin_app:all_users'))

        self.assertContains(response, self.export_url)
        self.assertContains(response, 'استخراج جميع المستخدمين إلى Excel')

    def test_export_is_a_complete_arabic_excel_workbook(self):
        self.client.force_login(self.staff)
        self.staff.profile.delete()

        response = self.client.get(self.export_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response['Content-Type'],
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        self.assertIn('.xlsx', response['Content-Disposition'])
        workbook = load_workbook(BytesIO(response.content), data_only=False)
        worksheet = workbook['المستخدمون']

        self.assertTrue(worksheet.sheet_view.rightToLeft)
        self.assertEqual(worksheet.freeze_panes, 'A5')
        headers = [cell.value for cell in worksheet[4]]
        self.assertIn('رقم الهاتف', headers)
        self.assertIn('النبذة الشخصية', headers)
        self.assertIn('عدد الطلبات', headers)
        self.assertNotIn('كلمة المرور', headers)

        rows = list(worksheet.iter_rows(min_row=5, values_only=True))
        customer_row = next(row for row in rows if row[0] == self.user.pk)
        self.assertEqual(customer_row[1], 'عميل-الوسام')
        self.assertEqual(customer_row[4], 'محمد علي')
        self.assertEqual(customer_row[6], '01012345678')
        self.assertEqual(customer_row[7], 'القاهرة، مدينة نصر')
        self.assertEqual(customer_row[8], 'عميل جملة')
        self.assertEqual(customer_row[18], 1)
        self.assertEqual(customer_row[20], 1)

        exported_ids = {row[0] for row in rows}
        self.assertEqual(exported_ids, {self.staff.pk, self.user.pk})
