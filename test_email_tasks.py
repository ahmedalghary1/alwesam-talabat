"""
سكريبت اختبار لنظام إرسال الإيميلات باستخدام Celery

هذا السكريبت يختبر جميع مهام الإيميلات للتأكد من عملها بشكل صحيح.
يجب تشغيل Redis و Celery worker قبل تشغيل هذا السكريبت.
"""

import os
import sys
import django

# إعداد Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from utils.email_tasks import (
    send_activation_email_task,
    send_order_confirmation_email_task,
    send_order_status_email_task
)
from accounts.models import CustomUser
from orders.models import Order


def test_connection():
    """اختبار الاتصال بـ Redis و Celery"""
    print("\n" + "="*60)
    print("🔍 اختبار الاتصال بـ Celery و Redis")
    print("="*60)
    
    try:
        from project.celery import app
        
        # اختبار الاتصال بـ Redis
        inspect = app.control.inspect()
        active = inspect.active()
        
        if active:
            print("✅ الاتصال بـ Celery worker ناجح")
            print(f"   عدد Workers النشطة: {len(active)}")
            return True
        else:
            print("❌ لم يتم العثور على Celery workers نشطة")
            print("   تأكد من تشغيل: celery -A project worker --loglevel=info --pool=solo")
            return False
            
    except Exception as e:
        print(f"❌ خطأ في الاتصال: {str(e)}")
        print("   تأكد من تشغيل Redis server")
        return False


def test_activation_email():
    """اختبار إيميل تفعيل الحساب"""
    print("\n" + "="*60)
    print("📧 اختبار إيميل تفعيل الحساب")
    print("="*60)
    
    try:
        # البحث عن أول مستخدم نشط
        user = CustomUser.objects.filter(is_active=True).first()
        
        if not user:
            print("❌ لم يتم العثور على مستخدمين نشطين")
            return False
        
        print(f"   المستخدم: {user.username} ({user.email})")
        
        # إرسال المهمة إلى Celery
        login_url = "http://localhost:8000/accounts/login/"
        result = send_activation_email_task.delay(user.id, login_url)
        
        print(f"   ✅ تم إرسال المهمة إلى قائمة الانتظار")
        print(f"   Task ID: {result.id}")
        print(f"   الحالة: {result.state}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ خطأ: {str(e)}")
        return False


def test_order_confirmation_email():
    """اختبار إيميل تأكيد الطلب"""
    print("\n" + "="*60)
    print("📧 اختبار إيميل تأكيد الطلب")
    print("="*60)
    
    try:
        # البحث عن آخر طلب
        order = Order.objects.select_related('user').order_by('-created_at').first()
        
        if not order:
            print("❌ لم يتم العثور على طلبات")
            print("   قم بإنشاء طلب من الموقع أولاً")
            return False
        
        print(f"   الطلب: #{order.id}")
        print(f"   العميل: {order.user.email}")
        print(f"   عدد المنتجات: {order.items.count()}")
        
        # إرسال المهمة
        result = send_order_confirmation_email_task.delay(order.id, order.user.email)
        
        print(f"   ✅ تم إرسال المهمة إلى قائمة الانتظار")
        print(f"   Task ID: {result.id}")
        print(f"   الحالة: {result.state}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ خطأ: {str(e)}")
        return False


def test_order_status_email():
    """اختبار إيميل تحديث حالة الطلب"""
    print("\n" + "="*60)
    print("📧 اختبار إيميل تحديث حالة الطلب")
    print("="*60)
    
    try:
        # البحث عن طلب
        order = Order.objects.select_related('user').filter(
            status__in=['pending', 'confirmed']
        ).first()
        
        if not order:
            print("❌ لم يتم العثور على طلبات مناسبة")
            return False
        
        print(f"   الطلب: #{order.id}")
        print(f"   العميل: {order.user.email}")
        print(f"   الحالة الحالية: {order.get_status_display()}")
        
        # اختبار إرسال إيميل بحالة "تم الشحن"
        test_status = 'shipped'
        result = send_order_status_email_task.delay(order.id, test_status, order.user.email)
        
        print(f"   ✅ تم إرسال المهمة إلى قائمة الانتظار")
        print(f"   الحالة الجديدة (محاكاة): تم الشحن")
        print(f"   Task ID: {result.id}")
        print(f"   ملاحظة: لن يتم تغيير حالة الطلب الفعلية - هذا اختبار فقط")
        
        return True
        
    except Exception as e:
        print(f"   ❌ خطأ: {str(e)}")
        return False


def check_email_settings():
    """التحقق من إعدادات البريد الإلكتروني"""
    print("\n" + "="*60)
    print("⚙️  التحقق من إعدادات البريد الإلكتروني")
    print("="*60)
    
    from django.conf import settings
    
    print(f"   EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"   EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"   EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"   EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"   EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"   DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    
    if 'console' in settings.EMAIL_BACKEND.lower():
        print("\n   ⚠️  تحذير: EMAIL_BACKEND مضبوط على console")
        print("   الإيميلات ستُطبع في console بدلاً من الإرسال الفعلي")
    
    return True


def main():
    """الدالة الرئيسية"""
    print("\n")
    print("╔" + "═"*58 + "╗")
    print("║" + " "*15 + "اختبار نظام إرسال الإيميلات" + " "*15 + "║")
    print("║" + " "*20 + "Celery Email Tasks" + " "*20 + "║")
    print("╚" + "═"*58 + "╝")
    
    # التحقق من إعدادات البريد
    check_email_settings()
    
    # اختبار الاتصال
    if not test_connection():
        print("\n❌ فشل الاتصال بـ Celery. توقف الاختبار.")
        print("\nتأكد من:")
        print("  1. تشغيل Redis: docker run -d -p 6379:6379 redis")
        print("  2. تشغيل Celery: celery -A project worker --loglevel=info --pool=solo")
        return
    
    # تشغيل الاختبارات
    results = {
        'activation': test_activation_email(),
        'order_confirmation': test_order_confirmation_email(),
        'order_status': test_order_status_email(),
    }
    
    # ملخص النتائج
    print("\n" + "="*60)
    print("📊 ملخص نتائج الاختبار")
    print("="*60)
    
    total = len(results)
    passed = sum(1 for r in results.values() if r)
    
    print(f"\n   إجمالي الاختبارات: {total}")
    print(f"   ✅ نجح: {passed}")
    print(f"   ❌ فشل: {total - passed}")
    
    if passed == total:
        print("\n   🎉 جميع الاختبارات نجحت!")
        print("\n   تحقق من:")
        print("   - Celery worker logs لرؤية تنفيذ المهام")
        print("   - صندوق البريد للإيميلات المرسلة")
    else:
        print("\n   ⚠️  بعض الاختبارات فشلت. راجع الأخطاء أعلاه.")
    
    print("\n" + "="*60)
    print("✅ انتهى الاختبار")
    print("="*60 + "\n")


if __name__ == '__main__':
    main()
