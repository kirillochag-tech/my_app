from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

class PasswordValidationTest(TestCase):
    def test_short_password_allowed(self):
        """Test that 4-character passwords are allowed (with proper complexity)"""
        try:
            validate_password('a1B!')  # 4 characters with different types should be allowed
            self.assertTrue(True)  # If no exception is raised, test passes
        except ValidationError:
            self.fail("4-character password should be allowed but was rejected")
    
    def test_3_char_password_rejected(self):
        """Test that 3-character passwords are rejected"""
        with self.assertRaises(ValidationError):
            validate_password('a1B')  # 3 characters should be rejected
    
    def test_user_creation_with_short_password(self):
        """Test that users can be created with 4-character passwords (with proper complexity)"""
        user = User.objects.create_user(
            username='testuser',
            password='a1B!',
            role='employee'
        )
        self.assertIsNotNone(user)
        self.assertTrue(user.check_password('a1B!'))