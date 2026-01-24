# 🐋 Docker Setup - الوسام طلبات

## نظرة عامة

هذا الدليل يشرح كيفية تشغيل المشروع باستخدام Docker مع:
- **PostgreSQL** - قاعدة البيانات
- **Redis** - Message broker لـ Celery
- **Django Web** - التطبيق الرئيسي
- **Celery Worker** - معالجة المهام غير المتزامنة
- **Celery Beat** - جدولة المهام

---

## المتطلبات الأساسية

- Docker Desktop (Windows/Mac) أو Docker Engine (Linux)
- Docker Compose

### تثبيت Docker (Windows)

1. حمّل Docker Desktop من: https://www.docker.com/products/docker-desktop
2. شغّل Docker Desktop
3. تأكد من تشغيل WSL 2 backend

---

## البدء السريع

### 1. بناء الـ Containers

```bash
docker-compose build
```

### 2. تشغيل جميع الخدمات

```bash
docker-compose up
```

أو للتشغيل في الخلفية:

```bash
docker-compose up -d
```

### 3. الوصول للتطبيق

- **Django App**: http://localhost:8000
- **Swagger API Docs**: http://localhost:8000/api/docs/
- **Django Admin**: http://localhost:8000/admin/
  - Username: `admin`
  - Password: `admin123`

---

## الأوامر المهمة

### عرض حالة الخدمات

```bash
docker-compose ps
```

### عرض Logs

```bash
# جميع الخدمات
docker-compose logs

# خدمة معينة
docker-compose logs web
docker-compose logs celery
docker-compose logs db

# متابعة logs مباشرة
docker-compose logs -f web
```

### إيقاف الخدمات

```bash
# إيقاف مع الحفاظ على الـ containers
docker-compose stop

# إيقاف وحذف الـ containers
docker-compose down

# إيقاف وحذف الـ containers + volumes (يحذف قاعدة البيانات!)
docker-compose down -v
```

### إعادة بناء الـ containers

```bash
# إعادة بناء بعد تعديل Dockerfile أو requirements.txt
docker-compose build --no-cache
docker-compose up -d
```

---

## إدارة قاعدة البيانات

### تشغيل Migrations

```bash
docker-compose exec web python manage.py migrate
```

### إنشاء Superuser جديد

```bash
docker-compose exec web python manage.py createsuperuser
```

### الوصول إلى Django Shell

```bash
docker-compose exec web python manage.py shell
```

### Backup قاعدة البيانات

```bash
docker-compose exec db pg_dump -U alwesam_user alwesam_db > backup.sql
```

### Restore قاعدة البيانات

```bash
docker-compose exec -T db psql -U alwesam_user alwesam_db < backup.sql
```

---

## اختبار API

### 1. التسجيل

```bash
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "phone": "01012345678",
    "address": "Test Address",
    "password": "testpass123",
    "password_confirm": "testpass123"
  }'
```

### 2. تفعيل المستخدم

```bash
# من Django shell
docker-compose exec web python manage.py shell

# ثم في Shell:
from accounts.models import CustomUser
user = CustomUser.objects.get(email='test@example.com')
user.is_active = True
user.save()
exit()
```

### 3. تسجيل الدخول

```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test@example.com",
    "password": "testpass123"
  }'
```

---

## المشاكل الشائعة وحلولها

### المشكلة: PostgreSQL لا يستجيب

```bash
# تحقق من حالة الـ container
docker-compose ps db

# تحقق من logs
docker-compose logs db

# إعادة تشغيل
docker-compose restart db
```

### المشكلة: Port 8000 مستخدم بالفعل

قم بتغيير البورت في `docker-compose.yml`:

```yaml
web:
  ports:
    - "8001:8000"  # بدلاً من 8000:8000
```

### المشكلة: Migrations فاشلة

```bash
# حذف قاعدة البيانات وإعادة إنشائها
docker-compose down -v
docker-compose up -d
docker-compose exec web python manage.py migrate
```

### المشكلة: Celery لا يعمل

```bash
# تحقق من Redis
docker-compose exec redis redis-cli ping

# تحقق من Celery logs
docker-compose logs celery

# إعادة تشغيل Celery
docker-compose restart celery
```

---

## تخصيص الإعدادات

### تعديل متغيرات البيئة

قم بتعديل ملف `.env`:

```env
# أمان
SECRET_KEY=your-super-secret-key-here

# Debug (False في Production)
DEBUG=False

# Allowed Hosts
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# قاعدة البيانات
DB_NAME=alwesam_db
DB_USER=alwesam_user
DB_PASSWORD=strong_password_here

# Email
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### تعديل docker-compose.yml

لزيادة Workers الخاصة بـ Celery:

```yaml
celery:
  command: celery -A project worker --loglevel=info --concurrency=4
```

---

## Development vs Production

### Development (الوضع الحالي)

- DEBUG=True
- SQLite أو PostgreSQL
- Django development server
- Hot reload enabled

### Production

قم بتعديل `.env`:

```env
DEBUG=False
ALLOWED_HOSTS=yourdomain.com
```

قم بتعديل `docker-compose.yml`:

```yaml
web:
  command: gunicorn project.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

---

## الـ Volumes

الـ Volumes المُستخدمة:

- `postgres_data`: بيانات PostgreSQL (persistent)
- `static_volume`: الملفات الثابتة (CSS, JS)
- `media_volume`: ملفات المستخدمين (صور، إلخ)

### عرض الـ Volumes

```bash
docker volume ls
```

### حذف الـ Volumes

```bash
docker volume rm alwesam-talabat_postgres_data
```

---

## الأمان

### في Production

1. **غيّر SECRET_KEY** في `.env`
2. **استخدم كلمات مرور قوية** لقاعدة البيانات
3. **اضبط DEBUG=False**
4. **حدد ALLOWED_HOSTS** بدقة
5. **استخدم HTTPS** (مع Nginx/Traefik)
6. **لا ترفع `.env`** على Git (موجود في .gitignore)

---

## الخدمات

| الخدمة | البورت | الوصف |
|--------|---------|-------|
| web | 8000 | Django Application |
| db | 5432 | PostgreSQL Database |
| redis | 6379 | Redis Cache/Broker |
| celery | - | Celery Worker |
| celery-beat | - | Celery Scheduler |

---

## الأوامر السريعة

```bash
# بناء وتشغيل
docker-compose up --build -d

# إيقاف كل شيء
docker-compose down

# إعادة تشغيل خدمة واحدة
docker-compose restart web

# عرض استهلاك الموارد
docker stats

# تنظيف (حذف containers، images، volumes غير المستخدمة)
docker system prune -a
```

---

## دعم

للمساعدة أو الإبلاغ عن مشاكل، راجع:
- [README.md](README.md) - التوثيق الرئيسي
- [docs/](docs/) - توثيق إضافي

---

**آخر تحديث:** يناير 2026  
**إصدار Docker:** 1.0
