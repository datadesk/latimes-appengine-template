import unittest

from django.core.exceptions import ValidationError

class ValidationTestCase(unittest.TestCase):
    def assertFailsValidation(self, clean, failed_fields):
        self.assertRaises(ValidationError, clean)
        try:
            clean()
        except ValidationError, e:
            self.assertEquals(sorted(failed_fields), sorted(e.message_dict.keys()))
    
    def assertFieldFailsValidationWithMessage(self, clean, field_name, message):
        self.assertRaises(ValidationError, clean)
        try:
            clean()
        except ValidationError, e:
            self.assertTrue(field_name in e.message_dict)
            self.assertEquals(message, e.message_dict[field_name])


