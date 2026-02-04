# مشروع الوسام - طلبات (Alwesam-Talabat)

## نظام تجارة إلكترونية للبيع بالجملة

نظام متكامل للبيع بالجملة بنظام الكرتونة مبني على Django 5.2.8

---

## 🚀 البدء السريع

### المتطلبات

- Python 3.10+
- Redis (لنظام Celery)
- التبعيات في `requirements.txt`

### التثبيت

```bash
# 1. Clone المشروع
cd alwesam-talabat1

# 2. إنشاء بيئة افتراضية
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 3. تثبيت المتطلبات
pip install -r requirements.txt

# 4. نسخ ملف البيئة
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/Mac
# قم بتعديل .env وضبط القيم المطلوبة

# 5. تطبيق Migrations
python manage.py migrate

# 6. إنشاء superuser
python manage.py createsuperuser

# 7. تشغيل Redis
docker run -d -p 6379:6379 --name redis-server redis
# أو قم بتشغيل Redis مباشرة إذا كان مثبتاً

# 8. تشغيل السيرفر والخوادم
# طريقة سريعة (Windows):
start_servers.bat

# أو يدوياً (افتح 3 terminals منفصلة):
# Terminal 1: Django Server
python manage.py runserver

# Terminal 2: Celery Worker (Windows)
celery -A project worker --loglevel=info --pool=solo

# Terminal 3: Celery Worker (Linux/Mac)
celery -A project worker --loglevel=info
```

افتح المتصفح: `http://localhost:8000`

### 🧪 اختبار نظام الإيميلات

```bash
python test_email_tasks.py
```

---

## 📂 هيكل المشروع

```
alwesam-talabat1/
├── accounts/          # إدارة المستخدمين والمصادقة
├── products/          # المنتجات والأقسام
├── cart/              # السلة
├── orders/            # الطلبات
├── home/              # الصفحة الرئيسية ولوحة التحكم الإدارية
├── utils/             # أدوات مساعدة
├── core/              # الثوابت
├── project/           # إعدادات Django
├── static/            # CSS, JS, Images
├── templates/         # قوالب HTML
├── media/             # ملفات المستخدمين
├── logs/              # السجلات
└── docs/              # التوثيق الكامل
```

---

## 🔧 التقنيات المستخدمة

### Backend

- Django 5.2.8
- **Celery 5.3+** (معالجة المهام غير المتزامنة)
- **Redis 5.0+** (Message broker لـ Celery)
- Pillow (معالجة الصور)
- python-decouple (إدارة البيئة)
- django-ratelimit (تحديد معدل الطلبات)
- django-debug-toolbar (أدوات التطوير)
- django-celery-results (حفظ نتائج مهام Celery)

### قاعدة البيانات

- SQLite (التطوير)
- PostgreSQL (الإنتاج - موصى به)

### Frontend

- HTML5
- CSS3 (بدون frameworks)
- JavaScript Vanilla

---

## ⚙️ التطبيقات (Django Apps)

### 1. accounts

- نموذج مستخدم مخصص (CustomUser)
- المصادقة بالإيميل أو الهاتف
- نظام موافقة الإدارة على المستخدمين الجدد
- إدارة الملف الشخصي والعناوين
- دعم الثيمات (فاتح/داكن)

### 2. products

- إدارة الأقسام والمنتجات
- دعم أنماط المنتجات (Variants)
- ألوان ومقاسات
- صور متعددة للمنتجات
- ضغط تلقائي للصور

### 3. cart

- سلة تسوق للمستخدمين المسجلين
- دعم localStorage للزوار
- مزامنة تلقائية عند تسجيل الدخول
- دعم القطع والكراتين

### 4. orders

- إنشاء وإدارة الطلبات
- تتبع حالة الطلب (pending, confirmed, shipped, delivered, cancelled)
- حفظ معلومات الأنماط عند الطلب
- سجل الطلبات للمستخدمين

### 5. home

- الصفحة الرئيسية
- لوحة تحكم إدارية مخصصة
- إدارة المنتجات والأقسام والطلبات
- نظام الموافقة على المستخدمين

---

## 🔐 المصادقة والأمان

### نظام المستخدمين

- تسجيل جديد → حساب غير مفعل (is_active=False)
- مراجعة الإدارة → موافقة أو رفض
- تسجيل دخول بالإيميل أو الهاتف
- Custom Authentication Backend

### الأمان

- Rate Limiting على تسجيل الدخول (5 محاولات/دقيقة)
- CSRF Protection
- Password Validation
- Session Security
- Middleware للتحقق من حالة المستخدمين

---

## 🗄️ قاعدة البيانات

### النماذج الأساسية (Models)

**accounts:**

- CustomUser (المستخدم الأساسي)
- Profile (الملف الشخصي)
- Address (العناوين)

**products:**

- Category (الأقسام)
- Product (المنتجات)
- ProductVariant (أنماط المنتجات)
- Color (الألوان)
- Size (المقاسات)
- ProductImages (صور إضافية)
- VariantImage (صور الأنماط)

**cart:**

- Cart (السلة)
- CartItem (عناصر السلة)

**orders:**

- Order (الطلب)
- OrderItem (عناصر الطلب)

---

## 🌐 الروابط الرئيسية (URLs)

### للمستخدمين

```
/                          - الصفحة الرئيسية
/products/                 - جميع الأقسام
/products/category/<slug>/ - منتجات قسم محدد
/products/product/<slug>/  - تفاصيل منتج
/products/search/          - بحث المنتجات

/cart/                     - عرض السلة
/cart/checkout/            - إتمام الطلب

/orders/                   - قائمة الطلبات
/orders/<id>/              - تفاصيل طلب

/accounts/signup/          - تسجيل جديد
/accounts/login/           - تسجيل دخول
/accounts/profile/         - الملف الشخصي
```

### للإدارة

```
/admin/                    - لوحة Django الافتراضية
/admin-panel/              - لوحة التحكم المخصصة
/admin-panel/products/     - إدارة المنتجات
/admin-panel/categories/   - إدارة الأقسام
/admin-panel/orders/       - إدارة الطلبات
/admin-panel/users/        - إدارة المستخدمين
```

---

## 🎨 المميزات

✅ نظام سلة تسوق ذكي مع AJAX  
✅ دعم localStorage للزوار  
✅ مزامنة تلقائية عند تسجيل الدخول  
✅ نظام موافقة إدارية على المستخدمين  
✅ دعم أنماط المنتجات (ألوان ومقاسات)  
✅ ضغط تلقائي للصور  
✅ دعم RTL للعربية  
✅ ثيم فاتح/داكن  
✅ تصميم متجاوب  
✅ لوحة تحكم إدارية مخصصة  
✅ بحث متقدم  
✅ تتبع حالة الطلبات  
✅ **نظام إيميلات غير متزامن مع Celery**  
✅ **إيميلات تفعيل + تأكيد طلبات + تحديث حالة**  

---

## 📧 نظام الإيميلات (Celery)

### أنواع الإيميلات

1. **إيميل تفعيل الحساب** - عند موافقة المشرف  
2. **إيميل تأكيد الطلب** - بعد إنشاء طلب جديد  
3. **إيميل تحديث الحالة** - عند تغيير حالة الطلب  

### المميزات

- ⚡ معالجة غير متزامنة (لا تؤثر على السرعة)
- 🔄 Retry تلقائي (3 محاولات)
- 📊 تسجيل كامل في قاعدة البيانات
- 📝 قوالب HTML responsive مع RTL

### التشغيل السريع

```bash
# تشغيل Redis
docker run -d -p 6379:6379 redis

# تشغيل Celery Worker (Windows)
celery -A project worker --loglevel=info --pool=solo

# اختبار النظام
python test_email_tasks.py
```

📚 **للتفاصيل الكاملة:** راجع [`docs/celery_setup.md`](docs/celery_setup.md)

---

## 📱 الواجهة الأمامية

### JavaScript

- `script.js` - الوظائف الأساسية (ثيم، لغة، animations)
- `cart-enhancements.js` - عمليات السلة
- `validation.js` - التحقق من الإدخال

### CSS

- 13 ملف CSS منظم
- نظام متغيرات CSS
- دعم Dark Mode
- تصميم متجاوب
- دعم RTL

---

## 🔧 الإعدادات

### ملف البيئة (.env)

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Custom User Model

```python
AUTH_USER_MODEL = 'accounts.CustomUser'
USERNAME_FIELD = 'email'
```

### Authentication Backends

```python
AUTHENTICATION_BACKENDS = [
    'accounts.backends.EmailPhoneBackend',
    'django.contrib.auth.backends.ModelBackend',
]
```

---

## 📊 لوحة التحكم الإدارية

### الوصول

- يتطلب حساب staff (`is_staff=True`)
- `/admin-panel/`

### المميزات

- إحصائيات (منتجات، أقسام، طلبات، مستخدمين)
- إدارة المنتجات (إضافة، تعديل، حذف)
- إدارة الأقسام
- إدارة الطلبات مع تحديث الحالة
- الموافقة/رفض المستخدمين الجدد
- بحث شامل

---

## 📝 ملاحظات مهمة

### المستخدمون الجدد

- الحسابات الجديدة تُنشأ غير مفعلة (is_active=False)
- يتطلب موافقة الإدارة قبل تسجيل الدخول
- يتم الموافقة من `/admin-panel/users/pending/`

### الطلبات

- الطلبات تُنشأ بحالة "pending"
- يمكن للمستخدم إلغاء الطلبات بحالة "pending" فقط
- الإدارة يمكنها تحديث حالة الطلب

### السلة

- المستخدمون المسجلون: حفظ في قاعدة البيانات
- الزوار: حفظ في localStorage
- مزامنة تلقائية عند تسجيل الدخول

---

## 📖 التوثيق الكامل

لمزيد من التفاصيل، راجع:

- **README_FULL.md** - توثيق كامل مدمج
- **docs/** - توثيق منفصل لكل قسم

---

## 🤝 المساهمة

1. قراءة التوثيق في مجلد `docs/`
2. اتباع معايير Django و PEP 8
3. كتابة tests للميزات الجديدة
4. تحديث التوثيق عند التغيير

---

**آخر تحديث:** يناير 2026  
**الإصدار:** 1.1 (مع دعم Celery)  
**Django:** 5.2.8  
**Python:** 3.10+  
**Celery:** 5.3+  
**Redis:** 5.0+
