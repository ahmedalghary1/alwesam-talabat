@echo off
REM ===================================================================
REM سكريبت Windows لتشغيل جميع خوادم المشروع
REM ===================================================================

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║           تشغيل مشروع الوسام طلبات                        ║
echo ║               Alwesam Talabat Project                      ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM التحقق من وجود Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python غير مثبت. يرجى تثبيت Python أولاً.
    pause
    exit /b 1
)

REM التحقق من وجود Redis
echo 🔍 التحقق من Redis...
redis-cli ping >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Redis غير متصل. جاري محاولة تشغيله...
    
    REM محاولة تشغيل Redis عبر Docker
    docker ps >nul 2>&1
    if errorlevel 1 (
        echo ❌ Docker غير متاح. يرجى تشغيل Redis يدوياً:
        echo    docker run -d -p 6379:6379 --name redis-server redis
        pause
        exit /b 1
    ) else (
        echo 🚀 تشغيل Redis في Docker...
        docker run -d -p 6379:6379 --name redis-server redis
        timeout /t 3 /nobreak >nul
    )
)

echo ✅ Redis متصل
echo.

REM تطبيق migrations إذا لزم الأمر
echo 📦 التحقق من قاعدة البيانات...
python manage.py migrate --check >nul 2>&1
if errorlevel 1 (
    echo 🔄 تطبيق migrations...
    python manage.py migrate
)

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║  سيتم فتح 3 نوافذ:                                        ║
echo ║  1. Django Server (port 8000)                             ║
echo ║  2. Celery Worker                                         ║
echo ║  3. Celery Monitor (Logs)                                 ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo اضغط أي زر للمتابعة...
pause >nul

REM تشغيل Django Server في نافذة جديدة
start "Django Server" cmd /k "echo 🌐 Django Server && python manage.py runserver"

REM الانتظار قليلاً قبل تشغيل Celery
timeout /t 2 /nobreak >nul

REM تشغيل Celery Worker في نافذة جديدة
start "Celery Worker" cmd /k "echo ⚡ Celery Worker && celery -A project worker --loglevel=info --pool=solo"

REM تشغيل مراقبة Celery logs
timeout /t 2 /nobreak >nul
start "Celery Monitor" cmd /k "echo 📊 Celery Monitor && echo. && echo راقب هذه النافذة لرؤية تنفيذ المهام... && echo. && timeout /t -1"

echo.
echo ✅ تم تشغيل جميع الخوادم!
echo.
echo 🌐 افتح المتصفح على: http://localhost:8000
echo.
echo لإيقاف الخوادم، أغلق جميع النوافذ المفتوحة.
echo.

pause
