from rest_framework import serializers
from .models import WalletTransaction, NFCCard
from decimal import Decimal

class WalletTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletTransaction
        fields = '__all__'
        read_only_fields = ('user', 'transaction_id', 'status', 'created_at')

class NFCCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = NFCCard
        fields = '__all__'
        read_only_fields = ('user', 'registered_at', 'last_used')

class AddFundsSerializer(serializers.Serializer):
    amount = serializers.DecimalField(
    max_digits=10,
    decimal_places=2,
    min_value=Decimal('100.00')  # Proper Decimal value
)
    payment_method = serializers.CharField(max_length=20)  # UPI, Card, NetBanking, etc.

class FASTagRegistrationSerializer(serializers.Serializer):
    fastag_id = serializers.CharField(max_length=100)
    vehicle_number = serializers.CharField(max_length=20)