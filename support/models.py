from django.db import models
from django.conf import settings


class CustomerMessage(models.Model):
    """رسائل العملاء إلى خدمة العملاء"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='customer_messages',
        verbose_name="المستخدم"
    )
    message = models.TextField(verbose_name="الرسالة")
    is_read = models.BooleanField(default=False, verbose_name="مقروءة")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإرسال")
    
    class Meta:
        verbose_name = "رسالة عميل"
        verbose_name_plural = "رسائل العملاء"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"رسالة من {self.user.username} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    @property
    def has_reply(self):
        """التحقق من وجود رد"""
        return self.replies.exists()
    
    @property
    def latest_reply(self):
        """أحدث رد"""
        return self.replies.first()


class MessageReply(models.Model):
    """ردود المسؤول على رسائل العملاء"""
    customer_message = models.ForeignKey(
        CustomerMessage,
        on_delete=models.CASCADE,
        related_name='replies',
        verbose_name="الرسالة الأصلية"
    )
    admin_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="المسؤول"
    )
    reply = models.TextField(verbose_name="الرد")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الرد")
    
    class Meta:
        verbose_name = "رد"
        verbose_name_plural = "الردود"
        ordering = ['created_at']
    
    def __str__(self):
        admin_name = self.admin_user.username if self.admin_user else "مسؤول محذوف"
        return f"رد من {admin_name} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
