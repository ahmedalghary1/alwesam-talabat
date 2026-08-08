from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import CustomerMessage, MessageReply


class FloatingSupportChatTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.customer = user_model.objects.create_user(
            username='support-customer',
            phone='01000000201',
            address='Cairo',
            password='StrongPass123!',
            is_active=True,
        )
        self.admin = user_model.objects.create_user(
            username='support-admin',
            phone='01000000202',
            address='Cairo',
            password='StrongPass123!',
            is_active=True,
            is_staff=True,
        )
        self.message = CustomerMessage.objects.create(
            user=self.customer,
            message='هل المنتج متوفر؟',
        )
        self.reply = MessageReply.objects.create(
            customer_message=self.message,
            admin_user=self.admin,
            reply='نعم، المنتج متوفر.',
        )
        self.client.force_login(self.customer)

    def test_messages_endpoint_returns_new_admin_replies_for_live_refresh(self):
        response = self.client.get(
            reverse('support:get_user_messages'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )

        self.assertEqual(response.status_code, 200)
        message = response.json()['messages'][0]
        self.assertEqual(message['id'], self.message.id)
        self.assertEqual(message['replies'][0]['id'], self.reply.id)
        self.assertEqual(message['replies'][0]['text'], 'نعم، المنتج متوفر.')
        self.assertIn('no-cache', response.headers['Cache-Control'])

    def test_messages_endpoint_does_not_expose_another_customer_conversation(self):
        user_model = get_user_model()
        other_customer = user_model.objects.create_user(
            username='other-customer',
            phone='01000000203',
            address='Giza',
            password='StrongPass123!',
            is_active=True,
        )
        CustomerMessage.objects.create(user=other_customer, message='رسالة خاصة')

        response = self.client.get(reverse('support:get_user_messages'))

        messages = response.json()['messages']
        self.assertEqual([message['id'] for message in messages], [self.message.id])
