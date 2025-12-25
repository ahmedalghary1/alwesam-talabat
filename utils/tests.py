"""
Tests for image compression utilities
"""
import os
import tempfile
from io import BytesIO
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from utils.image_utils import (
    generate_unique_filename,
    compress_image_to_webp,
    should_compress_image
)
from products.models import Category, Product, ProductImages
from accounts.models import Profile, CustomUser


class ImageUtilsTestCase(TestCase):
    """Test image utility functions"""
    
    def test_generate_unique_filename(self):
        """Test that generated filenames are unique"""
        filename1 = generate_unique_filename('test.jpg')
        filename2 = generate_unique_filename('test.jpg')
        
        # Filenames should be different
        self.assertNotEqual(filename1, filename2)
        
        # Both should end with .webp
        self.assertTrue(filename1.endswith('.webp'))
        self.assertTrue(filename2.endswith('.webp'))
    
    def test_should_compress_image(self):
        """Test image compression detection"""
        # Create a test image
        img = Image.new('RGB', (100, 100), color='red')
        img_io = BytesIO()
        img.save(img_io, 'JPEG')
        img_io.seek(0)
        
        # Create uploaded file
        uploaded_file = SimpleUploadedFile(
            name='test.jpg',
            content=img_io.read(),
            content_type='image/jpeg'
        )
        
        # Should compress non-WebP images
        self.assertTrue(should_compress_image(uploaded_file))
        
        # Create WebP image
        img_webp = BytesIO()
        img.save(img_webp, 'WEBP')
        img_webp.seek(0)
        
        uploaded_webp = SimpleUploadedFile(
            name='test.webp',
            content=img_webp.read(),
            content_type='image/webp'
        )
        
        # Should not compress WebP images
        self.assertFalse(should_compress_image(uploaded_webp))
    
    def test_compress_image_to_webp(self):
        """Test image compression to WebP"""
        # Create a large test image
        img = Image.new('RGB', (2500, 2500), color='blue')
        img_io = BytesIO()
        img.save(img_io, 'JPEG', quality=100)
        img_io.seek(0)
        
        original_size = len(img_io.getvalue())
        img_io.seek(0)
        
        # Create uploaded file
        uploaded_file = SimpleUploadedFile(
            name='large_image.jpg',
            content=img_io.read(),
            content_type='image/jpeg'
        )
        
        # Compress the image
        compressed = compress_image_to_webp(uploaded_file)
        
        # Verify compression
        self.assertIsNotNone(compressed)
        self.assertTrue(compressed.name.endswith('.webp'))
        
        # Compressed size should be smaller
        compressed_size = len(compressed.read())
        self.assertLess(compressed_size, original_size)
        
        # Verify image quality is maintained
        compressed.seek(0)
        compressed_img = Image.open(compressed)
        
        # Image should be resized to max dimensions
        self.assertLessEqual(compressed_img.width, 1920)
        self.assertLessEqual(compressed_img.height, 1920)


class CategoryImageCompressionTestCase(TestCase):
    """Test Category model image compression"""
    
    def test_category_image_compression(self):
        """Test that Category images are automatically compressed"""
        # Create a test image
        img = Image.new('RGB', (800, 600), color='green')
        img_io = BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        
        # Create uploaded file
        uploaded_file = SimpleUploadedFile(
            name='category_test.png',
            content=img_io.read(),
            content_type='image/png'
        )
        
        # Create category with image
        category = Category.objects.create(
            name='Test Category',
            image=uploaded_file
        )
        
        # Verify image was saved
        self.assertTrue(category.image)
        
        # Verify image is WebP format
        self.assertTrue(category.image.name.endswith('.webp'))


class ProductImageCompressionTestCase(TestCase):
    """Test Product model image compression"""
    
    def test_product_image_compression(self):
        """Test that Product images are automatically compressed"""
        # Create a test image
        img = Image.new('RGB', (1000, 800), color='yellow')
        img_io = BytesIO()
        img.save(img_io, 'JPEG')
        img_io.seek(0)
        
        # Create uploaded file
        uploaded_file = SimpleUploadedFile(
            name='product_test.jpg',
            content=img_io.read(),
            content_type='image/jpeg'
        )
        
        # Create product with image
        product = Product.objects.create(
            name='Test Product',
            pcs_carton=24,
            image=uploaded_file
        )
        
        # Verify image was saved
        self.assertTrue(product.image)
        
        # Verify image is WebP format
        self.assertTrue(product.image.name.endswith('.webp'))


class ProfileImageCompressionTestCase(TestCase):
    """Test Profile model image compression"""
    
    def test_profile_image_compression(self):
        """Test that Profile images are automatically compressed"""
        # Create user
        user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            phone='01234567890',
            address='Test Address'
        )
        
        # Create a test image
        img = Image.new('RGB', (500, 500), color='purple')
        img_io = BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        
        # Create uploaded file
        uploaded_file = SimpleUploadedFile(
            name='profile_test.png',
            content=img_io.read(),
            content_type='image/png'
        )
        
        # Create or update profile with image
        profile, created = Profile.objects.get_or_create(user=user)
        profile.image = uploaded_file
        profile.save()
        
        # Verify image was saved
        self.assertTrue(profile.image)
        
        # Verify image is WebP format
        self.assertTrue(profile.image.name.endswith('.webp'))
