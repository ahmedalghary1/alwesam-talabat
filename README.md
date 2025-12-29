# مشروع الوسام - طلبات (Alwesam-Talabat)

## نظام تجارة إلكترونية للبيع بالجملة

نظام متكامل للبيع بالجملة بنظام الكرتونة مبني على Django 5.2.8

---

## 🚀 البدء السريع

### المتطلبات

- Python 3.10+
- التبعيات في `requirements.txt`

### التثبيت

```bash
# 1. Clone المشروع
cd alwesam-talabat1

# 2. إنشاء بيئة افتراضية
python -m venv venv
venv\Scripts\activate

# 3. تثبيت المتطلبات
pip install -r requirements.txt

# 4. نسخ ملف البيئة
copy .env.example .env

# 5. تطبيق Migrations
python manage.py migrate

# 6. إنشاء superuser
python manage.py createsuperuser

# 7. تشغيل السيرفر
python manage.py runserver
```

افتح المتصفح: `http://localhost:8000`

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
- Pillow (معالجة الصور)
- python-decouple (إدارة البيئة)
- django-ratelimit (تحديد معدل الطلبات)
- django-debug-toolbar (أدوات التطوير)

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

**آخر تحديث:** ديسمبر 2025  
**الإصدار:** 1.0  
**Django:** 5.2.8  
**Python:** 3.10+
