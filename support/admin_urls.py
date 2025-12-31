from django.urls import path
from . import admin_views

app_name = 'admin_support'

urlpatterns = [
    path('messages/', admin_views.messages_list, name='messages_list'),
    path('messages/<int:message_id>/', admin_views.conversation_detail, name='conversation_detail'),
    path('messages/<int:message_id>/reply/', admin_views.send_reply, name='send_reply'),
    path('messages/<int:message_id>/mark-read/', admin_views.mark_as_read, name='mark_as_read'),
    path('messages/<int:message_id>/delete/', admin_views.delete_message, name='delete_message'),
]
