from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import UserProfile, LoyaltyProgram

User = get_user_model()

class UserModelTests(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            phone='+1234567890'
        )
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
        self.assertEqual(user.phone, '+1234567890')
        self.assertFalse(user.is_verified)
        
        # Check that profile and loyalty program were created
        self.assertTrue(hasattr(user, 'profile'))
        self.assertTrue(hasattr(user, 'loyalty'))

class UserViewsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            phone='+1234567890'
        )
    
    def test_user_registration(self):
        payload = {
            'email': 'new@example.com',
            'password': 'newpass123',
            'phone': '+1987654321',
            'user_type': 'CUSTOMER'
        }
        res = self.client.post('/api/users/register/', payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email='new@example.com')
        self.assertTrue(user.check_password('newpass123'))
    
    def test_user_login(self):
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        res = self.client.post('/api/users/login/', payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('access', res.data)
        self.assertIn('refresh', res.data)
    
    def test_get_user_profile(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.get('/api/users/profile/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['email'], self.user.email)