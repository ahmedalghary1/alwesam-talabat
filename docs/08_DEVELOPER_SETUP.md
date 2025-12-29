# Developer Setup Guide

## Overview

This guide will help developers set up the Alwesam-Talabat project on their local machine for development purposes.

---

## System Requirements

### Required Software

- **Python**: 3.10 or higher
- **pip**: Latest version
- **Git**: For version control
- **SQLite**: Included with Python (for development)
- **Web Browser**: Chrome, Firefox, or Edge (latest versions)

### Optional Software

- **PostgreSQL**: For production-like database testing
- **Redis**: For caching (optional in development)
- **VS Code** or **PyCharm**: Recommended IDEs

---

## Installation Steps

### 1. Clone the Repository

```bash
# Clone the project
git clone https://github.com/your-repo/alwesam-talabat.git
cd alwesam-talabat
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**requirements.txt contents**:

```
Django==5.2.8
Pillow
python-decouple==3.8
django-ratelimit==4.1.0
django-debug-toolbar==4.2.0
```

### 4. Environment Configuration

Create `.env` file in project root:

```bash
# Copy example file
cp .env.example .env

# Or create manually
```

**.env contents** (development):

```
SECRET_KEY=your-development-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

**Generate SECRET_KEY**:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 5. Database Setup

```bash
# Run migrations
python manage.py migrate

# Create superuser for admin access
python manage.py createsuperuser
```

Follow prompts to create superuser:

- Email: <your-email@example.com>
- Username: admin
- Phone: 1234567890
- Address: Test Address
- Password: (secure password)

### 6. Run Development Server

```bash
python manage.py runserver
```

Visit: `http://localhost:8000`

---

## Project Structure Overview

```
alwesam-talabat/
│
├── accounts/              # User authentication & profiles
│   ├── models.py         # CustomUser, Profile, Address
│   ├── views.py          # Login, signup, profile
│   ├── forms.py          # User forms
│   ├── backends.py       # Custom authentication
│   └── urls.py
│
├── products/             # Product catalog
│   ├── models.py         # Product, Category, Variant
│   ├── views.py          # Product listing, detail
│   └── admin.py          # Admin configuration
│
├── cart/                 # Shopping cart
│   ├── models.py         # Cart, CartItem
│   ├── views.py          # Cart operations
│   └── context_processors.py  # Global cart count
│
├── orders/               # Order processing
│   ├── models.py         # Order, OrderItem
│   └── views.py          # Order creation, history
│
├── home/                 # Homepage & admin panel
│   ├── views.py          # Homepage
│   ├── admin_views.py    # Custom admin panel
│   └── admin_urls.py     # Admin URL routing
│
├── utils/                # Shared utilities
│   ├── image_utils.py    # Image compression
│   └── decorators.py     # Custom decorators
│
├── core/                 # Constants & configuration
│   └── constants.py      # Global constants
│
├── project/              # Django project settings
│   ├── settings.py       # Main settings
│   ├── urls.py           # URL routing
│   └── wsgi.py           # WSGI config
│
├── static/               # Static assets
│   ├── css/              # Stylesheets
│   ├── js/               # JavaScript files
│   └── images/           # Static images
│
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── accounts/
│   ├── products/
│   ├── cart/
│   ├── orders/
│   └── admin/
│
├── media/                # User uploads (created on first upload)
├── logs/                 # Application logs (created automatically)
├── manage.py             # Django management script
├── requirements.txt      # Python dependencies
├── .env.example          # Example environment file
└── README.md             # Project documentation
```

---

## Creating Test Data

### Using Django Shell

```bash
python manage.py shell
```

**Create Categories**:

```python
from products.models import Category

Category.objects.create(
    name="إلكترونيات",
    description="الأجهزة الإلكترونية والكهربائية",
    image="path/to/image.jpg"
)
```

**Create Products**:

```python
from products.models import Product, Category

category = Category.objects.first()

Product.objects.create(
    name="منتج تجريبي",
    description="وصف المنتج التجريبي",
    pcs_carton=24,
    category=category,
    image="path/to/product_image.jpg",
    is_available=True
)
```

**Create Test User**:

```python
from accounts.models import CustomUser

user = CustomUser.objects.create_user(
    username="testuser",
    email="test@example.com",
    phone="1234567890",
    address="Test Address",
    password="testpassword123"
)
user.is_active = True  # Bypass admin approval for testing
user.save()
```

---

## Development Workflow

### 1. Start Development Session

```bash
# Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Pull latest changes
git pull origin main

# Install any new dependencies
pip install -r requirements.txt

# Run migrations (if any)
python manage.py migrate

# Start server
python manage.py runserver
```

### 2. Making Changes

**Database Model Changes**:

```bash
# 1. Edit models.py
# 2. Create migrations
python manage.py makemigrations

# 3. Review migration file in app/migrations/
# 4. Apply migrations
python manage.py migrate
```

**Template Changes**:

- Edit HTML files in `templates/`
- Changes reflect immediately (auto-reload)

**Static File Changes**:

- Edit CSS/JS in `static/`
- Hard refresh browser (Ctrl+F5)

**View Logic Changes**:

- Edit `views.py`
- Server auto-reloads
- Refresh browser

### 3. Testing Changes

```bash
# Run all tests
python manage.py test

# Test specific app
python manage.py test products

# Test specific class
python manage.py test products.tests.ProductModelTest
```

---

## Development Tools

### Django Debug Toolbar

Already included in `INSTALLED_APPS` when `DEBUG=True`.

**Usage**:

1. Run development server
2. Visit any page
3. Debug toolbar appears on right side
4. View SQL queries, templates, cache, etc.

### Django Shell

```bash
# Interactive Python shell with Django loaded
python manage.py shell

# Shell plus (if installed)
python manage.py shell_plus
```

### Database Management

```bash
# Access SQLite database
python manage.py dbshell

# Or use DB Browser for SQLite (GUI tool)
```

---

## Common Development Tasks

### Create New Django App

```bash
python manage.py startapp app_name
```

Then:

1. Add to `INSTALLED_APPS` in `settings.py`
2. Create models in `app_name/models.py`
3. Create migrations
4. Create views, URLs, templates

### Reset Database

```bash
# Delete database (WARNING: All data lost)
rm db.sqlite3

# Delete migrations (optional)
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete

# Recreate database
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### Generate Sample Data

Create `generate_data.py` management command:

```python
# accounts/management/commands/generate_data.py
from django.core.management.base import BaseCommand
from products.models import Category, Product
from faker import Faker

class Command(BaseCommand):
    def handle(self, *args, **options):
        fake = Faker()
        # Generate categories and products
        # ...
```

Run:

```bash
python manage.py generate_data
```

---

## Debugging Tips

### Print Debugging

```python
# In views
print(f"Debug: {variable_name}")

# Better: Use logging
import logging
logger = logging.getLogger(__name__)
logger.debug(f"Debug info: {variable_name}")
```

### Django Debug Toolbar

- Check SQL queries tab for N+1 problems
- Review template rendering time
- Inspect request/response data

### Browser DevTools

- Console: Check for JavaScript errors
- Network: Inspect AJAX requests
- Elements: Inspect DOM and CSS

### Database Queries

```python
# In Django shell
from django.db import connection
from products.models import Product

products = Product.objects.all()
print(connection.queries)  # Shows SQL queries
```

---

## Testing

### Run Tests

```bash
# All tests
python manage.py test

# Specific app
python manage.py test products

# With coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Generate HTML report
```

### Writing Tests

```python
# products/tests.py
from django.test import TestCase
from .models import Product, Category

class ProductModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name="Test Category",
            image="test.jpg"
        )
    
    def test_product_creation(self):
        product = Product.objects.create(
            name="Test Product",
            category=self.category,
            pcs_carton=24,
            image="test.jpg"
        )
        self.assertEqual(product.name, "Test Product")
        self.assertTrue(product.is_available)
```

---

## Code Style & Standards

### Python Code Style (PEP 8)

```bash
# Install flake8
pip install flake8

# Check code
flake8 accounts/ products/ cart/ orders/

# Auto-format with black
pip install black
black accounts/ products/ cart/ orders/
```

### HTML/CSS/JS

- Use 4 spaces for indentation (Python)
- Use 2 spaces for HTML/CSS/JS
- Keep lines under 120 characters
- Use meaningful variable names
- Comment complex logic

### Django Best Practices

- Use `get_object_or_404()` for single object retrieval
- Use `select_related()` and `prefetch_related()` for query optimization
- Always use `{% csrf_token %}` in forms
- Use transaction.atomic() for database operations
- Validate user inputs on server-side

---

## Git Workflow

### Branch Strategy

```bash
# Create feature branch
git checkout -b feature/feature-name

# Make changes and commit
git add .
git commit -m "Add feature description"

# Push to remote
git push origin feature/feature-name

# Create pull request on GitHub
# After review and approval, merge to main
```

### Commit Messages

```
feat: Add user approval workflow
fix: Resolve cart synchronization issue
docs: Update README with deployment instructions
style: Format code with black
refactor: Optimize product queries
test: Add tests for cart functionality
```

---

## IDE Setup

### VS Code

**Extensions**:

- Python
- Django
- Pylance
- GitLens
- Better Comments

**settings.json**:

```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true,
    "files.associations": {
        "*.html": "html",
        "*.css": "css"
    }
}
```

### PyCharm

1. Open project folder
2. Set interpreter: Settings → Project → Python Interpreter → Select venv
3. Enable Django support: Settings → Languages & Frameworks → Django
4. Set Django project root and settings file

---

## Troubleshooting

### Common Issues

**Issue**: ModuleNotFoundError
**Solution**: Ensure virtual environment is activated and dependencies installed

**Issue**: Database locked (SQLite)
**Solution**: Close all database connections, restart server

**Issue**: Static files not loading
**Solution**: Hard refresh browser (Ctrl+F5) or run `python manage.py collectstatic`

**Issue**: Migration conflicts
**Solution**:

```bash
python manage.py migrate --fake app_name migration_name
python manage.py migrate
```

**Issue**: Port 8000 in use
**Solution**:

```bash
# Use different port
python manage.py runserver 8001

# Or kill process using port
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

---

## Resources

### Documentation

- [Django Documentation](https://docs.djangoproject.com/)
- [Python Documentation](https://docs.python.org/)
- [Pillow Documentation](https://pillow.readthedocs.io/)

### Tutorials

- Django Girls Tutorial
- Real Python Django Tutorials
- Mozilla Django Tutorial

### Community

- Django Forum
- Stack Overflow (tag: django)
- Reddit: r/django

---

## Next Steps

After setup:

1. ✅ Explore the admin panel (`/admin-panel/`)
2. ✅ Create test categories and products
3. ✅ Test user registration and approval workflow
4. ✅ Test cart and checkout flow
5. ✅ Review code structure and documentation
6. ✅ Start contributing!

For detailed information on specific features, refer to the other documentation files in this directory.
