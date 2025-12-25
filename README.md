# مشروع الوسام - طلبات (Alwesam-Talabat)

## نظرة عامة
نظام تجارة إلكترونية متكامل للبيع بالجملة (بنظام الكرتونة) مبني على Django 5.2.8

## المميزات
- 🛒 نظام سلة تسوق ذكي مع دعم AJAX
- 📦 نظام طلبات متقدم
- 👤 إدارة مستخدمين مخصصة
- 🎨 دعم الوضع الداكن/الفاتح
- 🌐 دعم RTL للعربية
- 🔐 أمان محسّن مع Rate Limiting
- ⚡ أداء محسّن مع Caching
- 📊 لوحة تحكم إدارية شاملة

## المتطلبات
- Python 3.10+
- Django 5.2.8
- Pillow 10.0.0
- SQLite / PostgreSQL
- المزيد في `requirements.txt`

## التثبيت

### 1. استنساخ المشروع
```bash
git clone [repository-url]
cd alwesam-talabat/src
```

### 2. إنشاء بيئة افتراضية
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. تثبيت المتطلبات
```bash
pip install -r requirements.txt
```

### 4. إعداد متغيرات البيئة
انسخ `.env.example` إلى `.env` وقم بتحديث القيم:
```bash
copy .env.example .env  # Windows
# أو
cp .env.example .env   # Linux/Mac
```

ثم قم بتحرير `.env` وأضف مفتاح سري جديد:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 5. تطبيق الهجرة (Migrations)
```bash
python manage.py migrate
```

### 6. إنشاء مستخدم إداري
```bash
python manage.py createsuperuser
```

### 7. تشغيل المشروع
```bash
python manage.py runserver
```

الآن افتح المتصفح على: `http://localhost:8000`

## البنية المعمارية

```
src/
├── accounts/          # إدارة المستخدمين والمصادقة
├── products/          # المنتجات والأقسام
├── cart/              # السلة والعربة
├── orders/            # الطلبات
├── home/              # الصفحة الرئيسية ولوحة التحكم
├── utils/             # أدوات مساعدة
├── core/              # ثوابت المشروع
├── static/            # ملفات CSS, JS, Images
├── templates/         # قوالب HTML
├── media/             # ملفات المستخدمين المرفوعة
└── logs/              # ملفات السجلات

```

## الوحدات الرئيسية

### accounts
- مصادقة مخصصة بالبريد الإلكتروني
- ملفات شخصية للمستخدمين
- إدارة العناوين
- نظام الثيمات

### products
- إدارة المنتجات
- تصنيفات المنتجات
- معرض صور المنتجات
- بحث متقدم

### cart
- سلة مخصصة لكل مستخدم
- دعم  LocalStorage للزوار
- تحديث تلقائي بـ AJAX
- مزامنة تلقائية عند تسجيل الدخول

### orders
- إنشاء طلبات
- تتبع حالة الطلب
- سجل طلبات كامل
- لوحة تحكم إدارية

## API Endpoints

### المنتجات
- `GET /products/` - قائمة جميع الأقسام
- `GET /products/category/<slug>/` - منتجات قسم محدد
- `GET /products/product/<slug>/` - تفاصيل منتج
- `GET /products/search/` - بحث في المنتجات

### السلة
- `GET /cart/` - عرض السلة
- `POST /cart/add/<id>/` - إضافة منتج
- `POST /cart/remove/<id>/` - حذف منتج
- `POST /cart/update/<id>/` - تحديث كمية
- `POST /cart/sync/` - مزامنة من localStorage

### الطلبات
- `GET /orders/` - قائمة الطلبات
- `GET /orders/<id>/` - تفاصيل طلب
- `POST /orders/create/` - إنشاء طلب جديد
- `POST /orders/<id>/cancel/` - إلغاء طلب

### الحسابات
- `POST /accounts/login/` - تسجيل دخول
- `POST /accounts/signup/` - تسجيل جديد
- `GET /accounts/logout/` - تسجيل خروج
- `GET /accounts/profile/` - الملف الشخصي

## الإعدادات المتقدمة

### Caching
المشروع يستخدم Local Memory Cache مع timeout 15 دقيقة افتراضياً.
يمكن تغيير ذلك في `settings.py`:
```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'TIMEOUT': 900,  # 15 minutes
    }
}
```

### Logging
السجلات تحفظ في `logs/django.log` مع rotation تلقائي:
- حجم ملف: 5MB
- عدد النسخ الاحتياطية: 5
- مستوى السجل: INFO للتطوير, WARNING للإنتاج

### Rate Limiting
- تسجيل الدخول: 5 محاولات/دقيقة
- السلة: 30 طلب/دقيقة

## الاختبارات
```bash
# تشغيل جميع الاختبارات
python manage.py test

# اختبارات محددة
python manage.py test products
python manage.py test cart
python manage.py test accounts

# مع تغطية
coverage run --source='.' manage.py test
coverage report
```

## النشر (Production)

1. قم بتحديث `.env`:
```
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

2. جمع الملفات الثابتة:
```bash
python manage.py collectstatic
```

3. استخدم قاعدة بيانات إنتاجية (PostgreSQL موصى به):
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'alwesam_db',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

4. استخدم خادم WSGI (Gunicorn موصى به):
```bash
pip install gunicorn
gunicorn project.wsgi:application --bind 0.0.0.0:8000
```

## الأمان

- ✅ SECRET_KEY في متغيرات البيئة
- ✅ DEBUG=False في الإنتاج
- ✅ ALLOWED_HOSTS محدد
- ✅ CSRF Protection
- ✅ Rate Limiting على تسجيل الدخول
- ✅ Password Validation
- ✅ Secure Cookies (في الإنتاج)

## الدعم والمساهمة

للإبلاغ عن مشاكل أو اقتراحات، يرجى فتح Issue في المستودع.

## الترخيص

[حدد الترخيص هنا]

## المطورون

تم تطويده بواسطة فريق الوسام

---

**آخر تحديث**: 2025-12-18
