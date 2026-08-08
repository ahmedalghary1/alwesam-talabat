"""
Image compression and optimization utilities for Django models
Handles automatic conversion to WebP format with quality preservation
"""
import os
import uuid
from io import BytesIO
from datetime import datetime
from PIL import Image
from django.core.files.base import ContentFile
from django.db import transaction


def generate_unique_filename(original_filename, extension='webp'):
    """
    Generate a unique filename using UUID and timestamp to prevent duplicates
    
    Args:
        original_filename (str): The original filename
        extension (str): The desired file extension (default: 'webp')
    
    Returns:
        str: A unique filename in format: {uuid}_{timestamp}.{extension}
    """
    # Get the base name without extension
    base_name = os.path.splitext(os.path.basename(original_filename))[0]
    
    # Generate unique identifier
    unique_id = uuid.uuid4().hex[:12]  # Short UUID for readability
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Create unique filename
    unique_filename = f"{unique_id}_{timestamp}.{extension}"
    
    return unique_filename


def compress_image_to_webp(image_field, quality=85, max_width=1920, max_height=1920):
    """
    Compress and convert an image to WebP format with quality preservation
    
    Args:
        image_field: Django ImageField instance
        quality (int): WebP quality (0-100, default: 85)
        max_width (int): Maximum width in pixels (default: 1920)
        max_height (int): Maximum height in pixels (default: 1920)
    
    Returns:
        ContentFile: Compressed image as ContentFile, or None if compression fails
    """
    if not image_field:
        return None
    
    try:
        # Open the image
        img = Image.open(image_field)
        
        # Convert RGBA to RGB if necessary (for images with transparency)
        if img.mode == 'RGBA':
            # Create a white background
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])  # Use alpha channel as mask
            img = background
        elif img.mode not in ('RGB', 'L'):
            # Convert other modes to RGB
            img = img.convert('RGB')
        
        # Calculate new dimensions while maintaining aspect ratio
        original_width, original_height = img.size
        
        # Only resize if image is larger than max dimensions
        if original_width > max_width or original_height > max_height:
            # Calculate scaling factor
            width_ratio = max_width / original_width
            height_ratio = max_height / original_height
            scale_factor = min(width_ratio, height_ratio)
            
            # Calculate new dimensions
            new_width = int(original_width * scale_factor)
            new_height = int(original_height * scale_factor)
            
            # Resize with high-quality resampling
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Save to BytesIO in WebP format
        output = BytesIO()
        img.save(
            output,
            format='WEBP',
            quality=quality,
            method=6,  # Highest quality compression method
            optimize=True
        )
        output.seek(0)
        
        # Generate unique filename
        original_name = image_field.name if hasattr(image_field, 'name') else 'image'
        unique_filename = generate_unique_filename(original_name, 'webp')
        
        # Return as ContentFile
        return ContentFile(output.read(), name=unique_filename)
        
    except Exception as e:
        # Log the error (in production, use proper logging)
        print(f"Error compressing image: {str(e)}")
        return None


def should_compress_image(image_field):
    """
    Check if an image should be compressed
    
    Args:
        image_field: Django ImageField instance
    
    Returns:
        bool: True if image should be compressed, False otherwise
    """
    if not image_field:
        return False
    
    # Check if file exists and is not already WebP
    if hasattr(image_field, 'name') and image_field.name:
        # Skip if already WebP
        if image_field.name.lower().endswith('.webp'):
            return False
        return True
    
    return False


class ImageCompressionMixin:
    """Mixin to handle automatic image compression on save"""
    def save_with_compression(
        self,
        image_field_name='image',
        compression_options=None,
        *args,
        **kwargs,
    ):
        image_field = getattr(self, image_field_name, None)
        update_fields = kwargs.get('update_fields')
        image_is_being_saved = not update_fields or image_field_name in update_fields

        old_name = None
        if self.pk and image_is_being_saved:
            old_name = type(self)._base_manager.filter(pk=self.pk).values_list(
                image_field_name, flat=True
            ).first()

        # Compress before the database/storage save.  The previous implementation
        # saved twice, leaving the initially uploaded source file orphaned.
        if image_is_being_saved and image_field and should_compress_image(image_field):
            compressed_image = compress_image_to_webp(
                image_field,
                **(compression_options or {}),
            )
            if compressed_image:
                setattr(self, image_field_name, compressed_image)
        super().save(*args, **kwargs)

        new_field = getattr(self, image_field_name, None)
        new_name = getattr(new_field, 'name', None)
        if old_name and old_name != new_name:
            storage = new_field.storage
            transaction.on_commit(lambda: storage.delete(old_name))
