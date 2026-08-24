import shutil
import tempfile
from io import BytesIO

from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from api.v1.serializers.products import ProductDetailSerializer

from .models import (
    Category, Product, ProductSize, ProductSizeImage, ProductVariant, Size,
    VariantAttribute, VariantAttributeValue, VariantSize, VariantSizeImage,
)


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
        self.assertContains(
            response,
            'onclick="selectSizeOption(this)"',
        )
        self.assertContains(response, 'id="selected-size-label"')
        self.assertEqual(
            response.context['product_page_data']['directSizePrices'][0]['pcsCarton'],
            48,
        )
        self.assertContains(response, 'id="product-page-data"')

    def test_variants_sharing_a_color_remain_separate_storefront_options(self):
        product = Product.objects.create(
            name='منتج بنمطين', pcs_carton=24, image=_image_file()
        )
        color_attribute = VariantAttribute.objects.create(name='لون')
        black = VariantAttributeValue.objects.create(
            attribute=color_attribute,
            value='أسود',
            hex_code='#000000',
        )
        first_variant = ProductVariant.objects.create(
            product=product,
            name='النمط الأول',
        )
        second_variant = ProductVariant.objects.create(
            product=product,
            name='النمط الثاني',
        )
        first_variant.attributes.add(black)
        second_variant.attributes.add(black)

        response = self.client.get(
            reverse('products:product_detail', args=[product.slug])
        )

        variants = response.context['product_page_data']['variants']
        self.assertEqual([item['id'] for item in variants], [
            first_variant.id,
            second_variant.id,
        ])
        self.assertContains(response, "key = 'color_' + variant.id")
        self.assertContains(
            response,
            'variant.variantName || group.colorName',
        )

    def test_length_only_option_has_no_carton_quantity(self):
        product = Product.objects.create(
            name='خرطوم', length_label='الطول', image=_image_file()
        )
        length = Size.objects.create(name='20 متر')
        ProductSize.objects.create(product=product, size=length, pcs_carton=None)

        response = self.client.get(reverse('products:product_detail', args=[product.slug]))
        option = response.context['product_page_data']['directSizePrices'][0]
        api_data = ProductDetailSerializer(product).data['size_options'][0]
        endpoint = reverse('products:product_carton_quantity', args=[product.slug])
        endpoint_data = self.client.get(endpoint, {'size_id': length.pk}).json()

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(option['pcsCarton'])
        self.assertFalse(option['supportsCarton'])
        self.assertEqual(option['saleText'], 'يباع بالطول مباشرة')
        self.assertTrue(response.context['is_length_only_product'])
        self.assertContains(response, 'يباع بالطول مباشرة')
        self.assertContains(response, 'id="sale-method-row"')
        self.assertContains(response, 'id="pcs-carton-display">بالطول</strong>')
        self.assertNotContains(response, 'None قطعة/كرتون')
        self.assertIsNone(api_data['pcs_carton'])
        self.assertTrue(api_data['is_length_only'])
        self.assertFalse(endpoint_data['supports_carton'])
        self.assertEqual(endpoint_data['sale_text'], 'يباع بالطول مباشرة')

    def test_variant_length_only_option_never_renders_none_carton_text(self):
        product = Product.objects.create(
            name='خرطوم ملون', length_label='الطول', image=_image_file()
        )
        variant = ProductVariant.objects.create(product=product, name='أسود')
        length = Size.objects.create(name='30 متر')
        VariantSize.objects.create(variant=variant, size=length, pcs_carton=None)

        response = self.client.get(reverse('products:product_detail', args=[product.slug]))
        option = response.context['product_page_data']['variants'][0]['sizePrices'][0]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(option['saleText'], 'يباع بالطول مباشرة')
        self.assertTrue(response.context['is_length_only_product'])
        self.assertContains(response, 'id="pcs-carton-display">بالطول</strong>')
        self.assertNotContains(response, 'None قطعة/كرتون')

    def test_category_card_shows_length_instead_of_none_carton_quantity(self):
        category = Category.objects.create(name='خراطيم', image=_image_file())
        product = Product.objects.create(
            name='خرطوم 30 متر',
            category=category,
            length_label='الطول',
            image=_image_file(),
        )
        length = Size.objects.create(name='30 متر')
        ProductSize.objects.create(product=product, size=length, pcs_carton=None)

        response = self.client.get(reverse('products:category_products', args=[category.slug]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'الطول:')
        self.assertContains(response, '30 متر')
        self.assertContains(response, 'length-sale-meta')
        self.assertNotContains(response, 'None قطعة/كرتون')

    def test_card_sale_info_uses_length_only_variant_options(self):
        product = Product.objects.create(
            name='خرطوم بنمط', length_label='الطول', image=_image_file()
        )
        variant = ProductVariant.objects.create(product=product, name='أسود')
        length = Size.objects.create(name='50 متر')
        VariantSize.objects.create(variant=variant, size=length, pcs_carton=None)

        info = product.get_card_sale_info()

        self.assertTrue(info['is_length_only'])
        self.assertEqual(info['label'], 'الطول')
        self.assertEqual(info['values'], '50 متر')

    def test_direct_length_label_is_exposed_on_page_and_api(self):
        product = Product.objects.create(
            name='سلك', pcs_carton=24, length_label='الطول', image=_image_file()
        )
        size = Size.objects.create(name='2 متر')
        ProductSize.objects.create(product=product, size=size, pcs_carton=12)

        response = self.client.get(reverse('products:product_detail', args=[product.slug]))
        api_data = ProductDetailSerializer(product).data

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'اختر الطول')
        self.assertEqual(response.context['product_page_data']['product']['lengthLabel'], 'الطول')
        self.assertEqual(api_data['length_label'], 'الطول')

    def test_variant_inherits_product_length_label_when_its_label_is_blank(self):
        product = Product.objects.create(
            name='خرطوم', length_label='طول اللفة', image=_image_file()
        )
        variant = ProductVariant.objects.create(product=product, name='أحمر')

        data = ProductDetailSerializer(product).data

        self.assertEqual(variant.get_length_label(), 'طول اللفة')
        self.assertEqual(data['variants'][0]['length_label'], 'طول اللفة')

    def test_variant_size_quantity_is_sent_from_database(self):
        product = Product.objects.create(name='منتج بنمط', pcs_carton=24, image=_image_file())
        size = Size.objects.create(name='وسط')
        variant = ProductVariant.objects.create(product=product, name='نمط', pcs_carton=30)
        VariantSize.objects.create(variant=variant, size=size, pcs_carton=72)

        response = self.client.get(reverse('products:product_detail', args=[product.slug]))

        size_data = response.context['product_page_data']['variants'][0]['sizePrices'][0]
        self.assertEqual(size_data['sizeId'], size.pk)
        self.assertEqual(size_data['pcsCarton'], 72)

        endpoint = reverse('products:product_carton_quantity', args=[product.slug])
        quantity_response = self.client.get(endpoint, {
            'variant_id': variant.pk,
            'size_id': size.pk,
        })
        self.assertEqual(quantity_response.status_code, 200)
        self.assertEqual(quantity_response.json()['pcs_carton'], 72)
        self.assertEqual(quantity_response.json()['length_label'], 'المقاس')
        self.assertIn('no-store', quantity_response['Cache-Control'])

    def test_each_size_exposes_its_own_images_without_losing_quantity(self):
        product = Product.objects.create(name='Sized gallery', pcs_carton=24, image=_image_file())
        direct_size = Size.objects.create(name='Direct size')
        product_size = ProductSize.objects.create(
            product=product, size=direct_size, pcs_carton=48
        )
        direct_image = ProductSizeImage.objects.create(
            product_size=product_size, image=_image_file()
        )
        variant = ProductVariant.objects.create(product=product, name='Variant', pcs_carton=30)
        variant_size_name = Size.objects.create(name='Variant size')
        variant_size = VariantSize.objects.create(
            variant=variant, size=variant_size_name, pcs_carton=72
        )
        variant_image = VariantSizeImage.objects.create(
            variant_size=variant_size, image=_image_file()
        )

        response = self.client.get(reverse('products:product_detail', args=[product.slug]))

        direct_data = response.context['product_page_data']['directSizePrices'][0]
        variant_data = response.context['product_page_data']['variants'][0]['sizePrices'][0]
        self.assertEqual(direct_data['pcsCarton'], 48)
        self.assertEqual(direct_data['images'][0]['url'], direct_image.image.url)
        self.assertEqual(variant_data['pcsCarton'], 72)
        self.assertEqual(variant_data['images'][0]['url'], variant_image.image.url)
        self.assertContains(response, 'sizePrice?.images?.length')

        api_data = ProductDetailSerializer(product).data
        self.assertEqual(api_data['size_options'][0]['pcs_carton'], 48)
        self.assertTrue(api_data['size_options'][0]['images'][0]['image'])
        self.assertEqual(api_data['variants'][0]['size_options'][0]['pcs_carton'], 72)
        self.assertTrue(api_data['variants'][0]['size_options'][0]['images'][0]['image'])

    def test_direct_size_quantity_endpoint_reads_current_database_value(self):
        product = Product.objects.create(name='منتج مباشر', pcs_carton=24, image=_image_file())
        size = Size.objects.create(name='صغير')
        size_price = ProductSize.objects.create(product=product, size=size, pcs_carton=36)
        endpoint = reverse('products:product_carton_quantity', args=[product.slug])

        first_response = self.client.get(endpoint, {'size_id': size.pk})
        size_price.pcs_carton = 60
        size_price.save(update_fields=['pcs_carton'])
        second_response = self.client.get(endpoint, {'size_id': size.pk})

        self.assertEqual(first_response.json()['pcs_carton'], 36)
        self.assertEqual(second_response.json()['pcs_carton'], 60)

    def test_api_exposes_carton_quantity_for_each_size(self):
        product = Product.objects.create(name='منتج API', pcs_carton=24, image=_image_file())
        direct_size = Size.objects.create(name='مباشر')
        ProductSize.objects.create(product=product, size=direct_size, pcs_carton=40)
        variant = ProductVariant.objects.create(product=product, name='نمط API', pcs_carton=30)
        variant_size = Size.objects.create(name='نمط')
        VariantSize.objects.create(variant=variant, size=variant_size, pcs_carton=70)

        data = ProductDetailSerializer(product).data

        self.assertEqual(data['size_options'][0]['id'], direct_size.pk)
        self.assertEqual(data['size_options'][0]['pcs_carton'], 40)
        self.assertEqual(data['variants'][0]['size_options'][0]['id'], variant_size.pk)
        self.assertEqual(data['variants'][0]['size_options'][0]['pcs_carton'], 70)
