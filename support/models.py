from django.db import models
from django.conf import settings


class CustomerMessage(models.Model):
    """
    Customer messages to customer support
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='customer_messages',
        verbose_name="المستخدم"
    )
    message = models.TextField(verbose_name="الرسالة")
    sent_by_admin = models.BooleanField(default=False, verbose_name="مرسلة من الإدارة")
    admin_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='initiated_support_messages',
        verbose_name="المسؤول المرسل",
    )
    is_read = models.BooleanField(default=False, verbose_name="مقروءة")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإرسال")
    
    class Meta:
        verbose_name = "رسالة عميل"
        verbose_name_plural = "رسائل العملاء"
        ordering = ['-created_at']
    
    def __str__(self):
        sender = self.admin_user.username if self.sent_by_admin and self.admin_user else self.user.username
        return f"رسالة من {sender} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    @property
    def has_reply(self):
        """التحقق من وجود رد"""
        return self.replies.exists()
    
    @property
    def latest_reply(self):
        """أحدث رد"""
        return self.replies.first()


class MessageReply(models.Model):
    """
    Admin replies to customer messages
    """
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
