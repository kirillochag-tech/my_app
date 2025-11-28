from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from accounts.forms import CustomUserCreationForm

User = get_user_model()

class AuthTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_user_registration_and_login(self):
        """Тест регистрации пользователя и последующего входа в систему"""
        # Регистрация пользователя
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'employee',
            'phone': '+1234567890',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
        
        user = form.save()
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'testuser')
        
        # Проверяем, что пользователь может авторизоваться
        login_successful = self.client.login(username='testuser', password='testpass123')
        self.assertTrue(login_successful, "User should be able to login after registration")
        
        # Проверяем, что пользователь действительно существует и пароль корректно зашифрован
        user_from_db = User.objects.get(username='testuser')
        self.assertTrue(user_from_db.check_password('testpass123'))
        self.assertEqual(user_from_db.role, 'employee')
        self.assertEqual(user_from_db.phone, '+1234567890')

    def test_user_login_after_logout(self):
        """Тест входа в систему после выхода"""
        # Создаем пользователя
        user = User.objects.create_user(
            username='testuser2',
            password='testpass456',
            role='employee'
        )
        
        # Входим в систему
        login_response = self.client.post('/accounts/login/', {
            'username': 'testuser2',
            'password': 'testpass456'
        })
        
        # Проверяем, что вошли успешно
        self.assertEqual(login_response.status_code, 302)  # redirect after login
        
        # Выходим из системы
        logout_response = self.client.get('/accounts/logout/')
        self.assertEqual(logout_response.status_code, 302)
        
        # Снова входим в систему
        login_response_after_logout = self.client.post('/accounts/login/', {
            'username': 'testuser2',
            'password': 'testpass456'
        })
        
        # Проверяем, что снова успешно вошли
        self.assertEqual(login_response_after_logout.status_code, 302)

if __name__ == '__main__':
    import unittest
    unittest.main()