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


class OptionalEmailTests(TestCase):
    def setUp(self):
        self.user_model = get_user_model()

    def test_database_allows_multiple_users_without_email(self):
        first = self.user_model.objects.create_user(
            username='no-email-one',
            email=None,
            phone='01000000101',
            address='Cairo',
            password='StrongPass123!',
        )
        second = self.user_model.objects.create_user(
            username='no-email-two',
            email=None,
            phone='01000000102',
            address='Giza',
            password='StrongPass123!',
        )

        self.assertIsNone(first.email)
        self.assertIsNone(second.email)

    def test_api_registration_accepts_missing_email(self):
        serializer = RegisterSerializer(data={
            'username': 'api-no-email',
            'phone': '01000000103',
            'address': 'Cairo',
            'password': 'StrongPass123!',
            'password_confirm': 'StrongPass123!',
        })

        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()
        self.assertIsNone(user.email)
        self.assertFalse(user.is_active)

    def test_api_registration_endpoint_accepts_missing_email(self):
        response = self.client.post(
            reverse('api:auth-register'),
            {
                'username': 'api-endpoint-no-email',
                'phone': '01000000106',
                'address': 'Cairo',
                'password': 'StrongPass123!',
                'password_confirm': 'StrongPass123!',
            },
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 201, response.content)
        user = self.user_model.objects.get(username='api-endpoint-no-email')
        self.assertIsNone(user.email)
        self.assertFalse(user.is_active)

    def test_username_is_the_required_primary_identifier(self):
        self.assertEqual(self.user_model.USERNAME_FIELD, 'username')
        self.assertNotIn('email', self.user_model.REQUIRED_FIELDS)


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

    def test_signup_accepts_missing_email_and_keeps_it_optional(self):
        page = self.client.get(reverse('accounts:signup'))
        self.assertFalse(page.context['form'].fields['email'].required)
        self.assertContains(page, 'البريد الإلكتروني (اختياري)')

        response = self.client.post(reverse('accounts:signup'), {
            'username': 'web-no-email',
            'email': '',
            'phone': '01000000104',
            'address': 'Cairo',
            'password1': 'AnotherStrongPass123!',
            'password2': 'AnotherStrongPass123!',
        })

        self.assertRedirects(response, reverse('accounts:pending_approval'))
        user = self.user_model.objects.get(username='web-no-email')
        self.assertIsNone(user.email)
        self.assertFalse(user.is_active)

    def test_user_without_email_can_login_with_username(self):
        user = self.user_model.objects.create_user(
            username='username-only',
            email=None,
            phone='01000000105',
            address='Cairo',
            password='StrongPass123!',
            is_active=True,
        )

        response = self.client.post(reverse('accounts:login'), {
            'email': 'username-only',
            'password': 'StrongPass123!',
        })

        self.assertRedirects(response, reverse('home:home'))
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)

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
