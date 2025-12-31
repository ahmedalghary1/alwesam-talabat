from django.urls import path
from . import views

app_name = 'support'

urlpatterns = [
    path('send/', views.send_message, name='send_message'),
    path('messages/', views.get_user_messages, name='get_user_messages'),
    path('conversation/<int:message_id>/', views.get_conversation, name='get_conversation'),
]
