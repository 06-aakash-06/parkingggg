from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import WalletTransaction, NFCCard
from .services import PaymentService, NFCCardService

User = get_user_model()

class PaymentModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            phone='+1234567890'
        )
    
    def test_wallet_transaction(self):
        transaction = WalletTransaction.objects.create(
            user=self.user,
            amount=100.00,
            transaction_type='DEPOSIT',
            transaction_id='TXN123',
            status='SUCCESS'
        )
        self.assertEqual(transaction.user, self.user)
        self.assertEqual(transaction.amount, 100.00)

class PaymentServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            phone='+1234567890',
            wallet_balance=200.00
        )
    
    def test_successful_wallet_payment(self):
        success, transaction = PaymentService.process_wallet_payment(self.user, 50.00)
        self.assertTrue(success)
        self.assertEqual(transaction.amount, 50.00)
        self.assertEqual(self.user.wallet_balance, 150.00)
    
    def test_insufficient_balance(self):
        success, transaction = PaymentService.process_wallet_payment(self.user, 300.00)
        self.assertFalse(success)
        self.assertIsNone(transaction)
        self.assertEqual(self.user.wallet_balance, 200.00)

class NFCCardServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            phone='+1234567890'
        )
    
    def test_register_nfc_card(self):
        success, result = NFCCardService.register_nfc_card(self.user, 'NFC123')
        self.assertTrue(success)
        self.assertEqual(result.card_id, 'NFC123')
        self.assertEqual(self.user.nfc_card_id, 'NFC123')
    
    def test_duplicate_nfc_card(self):
        NFCCardService.register_nfc_card(self.user, 'NFC123')
        success, result = NFCCardService.register_nfc_card(self.user, 'NFC123')
        self.assertFalse(success)
        self.assertEqual(result, "Card already registered")

class PaymentViewsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            phone='+1234567890',
            wallet_balance=200.00
        )
        self.client.force_authenticate(user=self.user)
    
    def test_add_funds(self):
        payload = {
            'amount': 100.00,
            'payment_method': 'UPI'
        }
        res = self.client.post('/api/payments/wallet/add-funds/', payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.user.refresh_from_db()
        self.assertEqual(self.user.wallet_balance, 300.00)