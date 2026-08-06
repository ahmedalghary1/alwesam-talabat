#!/usr/bin/env python
"""
Create default superuser for Django project if no superuser exists.
This script is idempotent - it can be run multiple times safely.
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()


def create_default_superuser():
    """Create default superuser if no superuser exists."""
    
    # Check if any superuser already exists
    if User.objects.filter(is_superuser=True).exists():
        print("✅ Superuser already exists, skipping creation.")
        print(f"   Total superusers: {User.objects.filter(is_superuser=True).count()}")
        return True
    
    # Get superuser credentials from environment variables with defaults
    username = os.getenv('DJANGO_SUPERUSER_USERNAME', 'admin')
    email = os.getenv('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
    password = os.getenv('DJANGO_SUPERUSER_PASSWORD')
    phone = os.getenv('DJANGO_SUPERUSER_PHONE', '01000000000')
    address = os.getenv('DJANGO_SUPERUSER_ADDRESS', 'Admin Address')
    
    if not password:
        print("❌ DJANGO_SUPERUSER_PASSWORD must be set; refusing to create an insecure default admin.")
        return False

    try:
        # Create the superuser
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            phone=phone,
            address=address
        )
        
        print("✅ Default superuser created successfully!")
        print(f"   Username: {username}")
        print(f"   Email: {email}")
        print("   🔗 Access admin at: http://localhost:8000/admin/")
        
        return True
        
    except Exception as e:
        print(f"❌ Could not create superuser: {e}")
        print("   This is not critical - you can create superuser manually later.")
        print("   Use: docker-compose exec web python manage.py createsuperuser")
        return False


if __name__ == "__main__":
    success = create_default_superuser()
    sys.exit(0 if success else 1)
