from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.db import IntegrityError, transaction
from django.test import TestCase, override_settings
from django.urls import reverse

from api.v1.serializers.accounts import RegisterSerializer


class PhoneUniquenessTests(TestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.user_model.objects.create_user(
            username='first',
            email='first@example.com',
            phone='01000000001',
            address='test',
            password='password',
        )

    def test_database_rejects_duplicate_phone(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            self.user_model.objects.create_user(
                username='second',
                email='second@example.com',
                phone='01000000001',
                address='test',
                password='password',
            )

    def test_api_registration_rejects_duplicate_phone(self):
        serializer = RegisterSerializer(data={
            'username': 'second',
            'email': 'second@example.com',
            'phone': '01000000001',
            'address': 'test',
            'password': 'password123',
            'password_confirm': 'password123',
        })

        self.assertFalse(serializer.is_valid())
        self.assertIn('phone', serializer.errors)


@override_settings(RATELIMIT_ENABLE=False)
class AccountPageTests(TestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.active_user = self.user_model.objects.create_user(
            username='active-user',
            email='active@example.com',
            phone='01000000002',
            address='Cairo',
            password='StrongPass123!',
            is_active=True,
        )

    def test_signup_creates_inactive_account_and_shows_success_immediately(self):
        response = self.client.post(reverse('accounts:signup'), {
            'username': 'new-user',
            'email': 'NEW@example.com',
            'phone': '01000000003',
            'address': 'Giza',
            'password1': 'AnotherStrongPass123!',
            'password2': 'AnotherStrongPass123!',
        }, follow=True)

        self.assertRedirects(response, reverse('accounts:pending_approval'))
        new_user = self.user_model.objects.get(email='new@example.com')
        self.assertFalse(new_user.is_active)
        self.assertContains(response, 'تم إنشاء حسابك بنجاح')
        self.assertIn(
            'تم إنشاء حسابك بنجاح وإرساله إلى المسؤول للمراجعة.',
            [str(message) for message in get_messages(response.wsgi_request)],
        )

    def test_invalid_signup_keeps_entered_address_and_shows_password_error(self):
        response = self.client.post(reverse('accounts:signup'), {
            'username': 'new-user',
            'email': 'new@example.com',
            'phone': '01000000003',
            'address': 'العنوان المدخل',
            'password1': 'one-password',
            'password2': 'different-password',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'كلمتا المرور غير متطابقتين')
        self.assertContains(response, 'العنوان المدخل')
        self.assertFalse(self.user_model.objects.filter(email='new@example.com').exists())

    def test_login_accepts_email_case_insensitively(self):
        response = self.client.post(reverse('accounts:login'), {
            'email': 'ACTIVE@EXAMPLE.COM',
            'password': 'StrongPass123!',
        })

        self.assertRedirects(response, reverse('home:home'))
        self.assertEqual(int(self.client.session['_auth_user_id']), self.active_user.pk)

    def test_login_accepts_username_case_insensitively(self):
        response = self.client.post(reverse('accounts:login'), {
            'email': 'ACTIVE-USER',
            'password': 'StrongPass123!',
        })

        self.assertRedirects(response, reverse('home:home'))
        self.assertEqual(int(self.client.session['_auth_user_id']), self.active_user.pk)

    def test_login_does_not_accept_phone_number(self):
        response = self.client.post(reverse('accounts:login'), {
            'email': '01000000002',
            'password': 'StrongPass123!',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'البريد الإلكتروني/اسم المستخدم أو كلمة المرور غير صحيحة')
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_failed_login_keeps_identifier_visible(self):
        response = self.client.post(reverse('accounts:login'), {
            'email': 'active@example.com',
            'password': 'wrong-password',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'active@example.com')
        self.assertContains(response, 'البريد الإلكتروني/اسم المستخدم أو كلمة المرور غير صحيحة')
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_inactive_account_gets_pending_approval_message(self):
        self.active_user.is_active = False
        self.active_user.save(update_fields=['is_active'])

        response = self.client.post(reverse('accounts:login'), {
            'email': self.active_user.email,
            'password': 'StrongPass123!',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'حسابك في انتظار موافقة المسؤول')
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_login_rejects_external_next_url(self):
        response = self.client.post(
            reverse('accounts:login') + '?next=https://example.org/phishing',
            {'email': self.active_user.email, 'password': 'StrongPass123!'},
        )

        self.assertRedirects(response, reverse('home:home'))
