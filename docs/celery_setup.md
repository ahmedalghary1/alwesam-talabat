# دليل تشغيل Celery للمشروع

## نظرة عامة

يستخدم هذا المشروع **Celery** مع **Redis** لمعالجة المهام غير المتزامنة (Asynchronous Tasks)، خاصةً إرسال الإيميلات في الخلفية.

---

## المتطلبات

### 1. تثبيت المكتبات المطلوبة

```bash
pip install -r requirements.txt
```

هذا سيثبت:

- `celery>=5.3.0` - نظام المهام الموزع
- `redis>=5.0.0` - Message broker
- `django-celery-results>=2.5.0` - لحفظ نتائج المهام

### 2. تثبيت وتشغيل Redis

#### على Windows

**الطريقة الأولى: باستخدام Docker (الأسهل)**

```bash
# تشغيل Redis في Docker
docker run -d -p 6379:6379 --name redis-server redis:latest

# للتحقق من أن Redis يعمل
docker ps
```

**الطريقة الثانية: تحميل Redis ل Windows**

1. حمّل Redis من: <https://github.com/microsoftarchive/redis/releases>
2. شغّل `redis-server.exe`

#### على Linux/Mac

```bash
# تثبيت Redis
sudo apt-get install redis-server  # Ubuntu/Debian
brew install redis                  # macOS

# تشغيل Redis
redis-server
```

#### التحقق من Redis

```bash
# افتح terminal جديد واختبر الاتصال
redis-cli ping
# يجب أن ترى: PONG
```

---

## خطوات التشغيل

### 1. تشغيل Redis Server

تأكد من أن Redis يعمل أولاً (انظر القسم أعلاه).

### 2. تطبيق Migrations لقاعدة البيانات

يجب تطبيق migrations لـ `django-celery-results`:

```bash
python manage.py migrate
```

### 3. تشغيل Django Development Server

في terminal منفصل:

```bash
python manage.py runserver
```

### 4. تشغيل Celery Worker

**على Windows:**

```bash
celery -A project worker --loglevel=info --pool=solo
```

**على Linux/Mac:**

```bash
celery -A project worker --loglevel=info
```

> **ملاحظة**: خيار `--pool=solo` ضروري على Windows لأن Celery لا يدعم multiprocessing pool على Windows بشكل كامل.

---

## التحقق من عمل النظام

### 1. فحص الاتصال بـ Redis

```bash
redis-cli ping
# Output: PONG
```

### 2. اختبار Celery Worker

عند تشغيل Celery worker، يجب أن ترى output مشابه لـ:

```
 -------------- celery@YOUR-COMPUTER v5.3.x
---- **** ----- 
--- * ***  * -- Windows-10.0.xxxxx
-- * - **** --- 
- ** ---------- [config]
- ** ---------- .> app:         project:0x...
- ** ---------- .> transport:   redis://localhost:6379/0
- ** ---------- .> results:     django-db
- *** --- * --- .> concurrency: 1 (solo)
-- ******* ---- .> task events: OFF
--- ***** ----- 
 -------------- [queues]
                .> celery           exchange=celery(direct) key=celery

[tasks]
  . utils.email_tasks.send_activation_email_task
  . utils.email_tasks.send_order_confirmation_email_task
  . utils.email_tasks.send_order_status_email_task
```

### 3. اختبار إرسال إيميل

1. **اختبار تفعيل مستخدم:**
   - سجل مستخدم جديد
   - ادخل كمشرف إلى `/admin/pending-users/`
   - وافق على المستخدم
   - راقب logs Celery - يجب أن ترى:

     ```
     [INFO/MainProcess] Task utils.email_tasks.send_activation_email_task[xxx] received
     [INFO/MainProcess] Activation email sent successfully to user@example.com
     [INFO/MainProcess] Task utils.email_tasks.send_activation_email_task[xxx] succeeded
     ```

2. **اختبار تأكيد طلب:**
   - قم بإنشاء طلب جديد من المتجر
   - راقب logs Celery للتأكد من إرسال الإيميل

3. **اختبار تحديث حالة طلب:**
   - من لوحة الإدارة، غير حالة طلب موجود
   - راقب logs Celery

---

## إعدادات متقدمة

### استخدام متغيرات البيئة

يمكنك تغيير عنوان Redis عبر ملف `.env`:

```env
CELERY_BROKER_URL=redis://localhost:6379/0
```

للإنتاج (Production)، قد تستخدم Redis خارجي:

```env
CELERY_BROKER_URL=redis://your-redis-host:6379/0
```

### مراقبة Celery باستخدام Flower

Flower هي أداة مراقبة في الوقت الفعلي لـ Celery:

```bash
# تثبيت
pip install flower

# تشغيل
celery -A project flower

# افتح المتصفح على: http://localhost:5555
```

---

## حل المشاكل الشائعة

### 1. خطأ: "Cannot connect to redis"

**الحل:** تأكد من تشغيل Redis server أولاً.

### 2. خطأ: "Task not registered"

**الحل:**

- تأكد من أن الـ tasks في ملف `utils/email_tasks.py`
- أعد تشغيل Celery worker

### 3. الإيميلات لا تُرسل

**الحل:**

- تحقق من إعدادات SMTP في `settings.py`
- راجع logs Celery للأخطاء
- تحقق من صحة بيانات `EMAIL_HOST_USER` و `EMAIL_HOST_PASSWORD`

### 4. على Windows: "AttributeError: 'module' object has no attribute 'poll'"

**الحل:** استخدم `--pool=solo` عند تشغيل Celery worker.

---

## للإنتاج (Production)

### استخدام Supervisor لإدارة Celery

إنشاء ملف `/etc/supervisor/conf.d/celery.conf`:

```ini
[program:celery]
command=/path/to/venv/bin/celery -A project worker --loglevel=info
directory=/path/to/project
user=www-data
numprocs=1
stdout_logfile=/var/log/celery/worker.log
stderr_logfile=/var/log/celery/worker.log
autostart=true
autorestart=true
startsecs=10
stopwaitsecs=600
```

ثم:

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start celery
```

### استخدام systemd

إنشاء ملف `/etc/systemd/system/celery.service`:

```ini
[Unit]
Description=Celery Service
After=network.target

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/path/to/project
ExecStart=/path/to/venv/bin/celery -A project worker --loglevel=info

[Install]
WantedBy=multi-user.target
```

ثم:

```bash
sudo systemctl daemon-reload
sudo systemctl enable celery
sudo systemctl start celery
```

---

## أوامر مفيدة

```bash
# فحص حالة Celery
celery -A project inspect active

# عرض المهام المسجلة
celery -A project inspect registered

# إيقاف جميع workers
celery -A project control shutdown

# مسح جميع المهام من القائمة
celery -A project purge
```

---

## الخلاصة

الآن، جميع عمليات إرسال الإيميلات تعمل في الخلفية:

- ✅ تفعيل الحساب
- ✅ تأكيد الطلب
- ✅ تحديث حالة الطلب

هذا يضمن:

- **استجابة سريعة** للمستخدمين
- **موثوقية أعلى** مع إمكانية إعادة المحاولة
- **قابلية التوسع** لمعالجة آلاف الإيميلات
