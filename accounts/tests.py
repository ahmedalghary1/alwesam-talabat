from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase

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
