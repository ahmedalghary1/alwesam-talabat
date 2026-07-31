from django.test import SimpleTestCase

from .admin_views import _valid_model_ids


class ValidModelIdsTests(SimpleTestCase):
    def test_ignores_blank_and_invalid_values(self):
        self.assertEqual(
            _valid_model_ids(['', '  ', 'invalid', None, '7']),
            [7],
        )

    def test_accepts_only_positive_integer_ids(self):
        self.assertEqual(
            _valid_model_ids(['1', '0', '-2', '3']),
            [1, 3],
        )

# Create your tests here.
