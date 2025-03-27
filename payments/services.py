import requests
from django.conf import settings
from django.utils import timezone
from .models import WalletTransaction, NFCCard

class PaymentService:
    @staticmethod
    def process_wallet_payment(user, amount):
        """
        Process payment using user's wallet balance
        """
        if user.wallet_balance >= amount:
            user.wallet_balance -= amount
            user.save()
            
            transaction = WalletTransaction.objects.create(
                user=user,
                amount=amount,
                transaction_type='PAYMENT',
                transaction_id=f"WALLET{timezone.now().timestamp()}",
                status='SUCCESS',
                description='Payment from wallet'
            )
            
            return True, transaction
        return False, None

class NFCCardService:
    @staticmethod
    def register_nfc_card(user, card_id):
        """
        Register a new NFC card for a user
        """
        if NFCCard.objects.filter(card_id=card_id).exists():
            return False, "Card already registered"
        
        card = NFCCard.objects.create(
            user=user,
            card_id=card_id
        )
        
        # Update user's primary NFC card if not set
        if not user.nfc_card_id:
            user.nfc_card_id = card_id
            user.save()
        
        return True, card

    @staticmethod
    def process_nfc_payment(card_id, amount):
        """
        Process payment using NFC card
        """
        try:
            card = NFCCard.objects.get(card_id=card_id, is_active=True)
            
            # In a real implementation, this would call the NFC payment gateway
            # For demo purposes, we'll simulate a successful payment
            
            transaction = WalletTransaction.objects.create(
                user=card.user,
                amount=amount,
                transaction_type='PAYMENT',
                transaction_id=f"NFC{timezone.now().timestamp()}",
                status='SUCCESS',
                description='Payment via NFC card'
            )
            
            # Update last used time
            card.last_used = timezone.now()
            card.save()
            
            return True, transaction
        except NFCCard.DoesNotExist:
            return False, "Invalid or inactive NFC card"