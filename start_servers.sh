#!/bin/bash
# ===================================================================
# سكريبت Linux/Mac لتشغيل جميع خوادم المشروع
# ===================================================================

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║           تشغيل مشروع الوسام طلبات                        ║"
echo "║               Alwesam Talabat Project                      ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# التحقق من وجود Python
if ! command -v python &> /dev/null; then
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python غير مثبت. يرجى تثبيت Python أولاً."
        exit 1
    else
        PYTHON_CMD="python3"
    fi
else
    PYTHON_CMD="python"
fi

# التحقق من وجود Redis
echo "🔍 التحقق من Redis..."
if ! redis-cli ping &> /dev/null; then
    echo "⚠️  Redis غير متصل. جاري محاولة تشغيله..."
    
    # محاولة تشغيل Redis عبر Docker
    if command -v docker &> /dev/null; then
        echo "🚀 تشغيل Redis في Docker..."
        docker run -d -p 6379:6379 --name redis-server redis
        sleep 3
    else
        echo "❌ Docker غير متاح. يرجى تشغيل Redis يدوياً:"
        echo "   sudo systemctl start redis"
        echo "   أو: docker run -d -p 6379:6379 redis"
        exit 1
    fi
fi

echo "✅ Redis متصل"
echo ""

# تطبيق migrations إذا لزم الأمر
echo "📦 التحقق من قاعدة البيانات..."
$PYTHON_CMD manage.py migrate --check &> /dev/null
if [ $? -ne 0 ]; then
    echo "🔄 تطبيق migrations..."
    $PYTHON_CMD manage.py migrate
fi

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  سيتم فتح 3 terminals:                                    ║"
echo "║  1. Django Server (port 8000)                             ║"
echo "║  2. Celery Worker                                         ║"
echo "║  3. Celery Logs Monitor                                   ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# تشغيل Django Server
gnome-terminal --title="Django Server" -- bash -c "$PYTHON_CMD manage.py runserver; exec bash" 2>/dev/null || \
xterm -e "$PYTHON_CMD manage.py runserver" 2>/dev/null || \
konsole -e "$PYTHON_CMD manage.py runserver" 2>/dev/null &

sleep 2

# تشغيل Celery Worker
gnome-terminal --title="Celery Worker" -- bash -c "celery -A project worker --loglevel=info; exec bash" 2>/dev/null || \
xterm -e "celery -A project worker --loglevel=info" 2>/dev/null || \
konsole -e "celery -A project worker --loglevel=info" 2>/dev/null &

echo ""
echo "✅ تم تشغيل جميع الخوادم!"
echo ""
echo "🌐 افتح المتصفح على: http://localhost:8000"
echo ""
echo "لإيقاف الخوادم:"
echo "  - اضغط Ctrl+C في كل terminal"
echo "  أو استخدم: pkill -f 'manage.py runserver' && pkill -f 'celery'"
echo ""
