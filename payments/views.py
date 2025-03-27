from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import WalletTransaction, NFCCard
from .serializers import (
    WalletTransactionSerializer,
    NFCCardSerializer,
    AddFundsSerializer,
    FASTagRegistrationSerializer
)
from users.models import User
import time
from django.utils import timezone

# Template Views
@login_required
def wallet(request):
    transactions = WalletTransaction.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'wallet_balance': request.user.wallet_balance,
        'transactions': transactions
    }
    return render(request, 'payment/wallet.html', context)

@login_required
def add_funds(request):
    if request.method == 'POST':
        try:
            amount = float(request.POST.get('amount'))
            payment_method = request.POST.get('payment_method')
            
            if amount <= 0:
                messages.error(request, 'Amount must be positive')
                return redirect('wallet')
            
            # Create transaction
            transaction = WalletTransaction.objects.create(
                user=request.user,
                amount=amount,
                transaction_type='DEPOSIT',
                transaction_id=f"WALLET{int(time.time())}",
                status='SUCCESS',
                description=f"Wallet top-up via {payment_method}"
            )
            
            # Update balance
            request.user.wallet_balance += amount
            request.user.save()
            
            messages.success(request, f'Successfully added ₹{amount:.2f} to your wallet')
            return redirect('wallet')
        
        except ValueError:
            messages.error(request, 'Invalid amount')
    
    return redirect('wallet')

@login_required
def payment_methods(request):
    nfc_cards = NFCCard.objects.filter(user=request.user)
    context = {
        'nfc_cards': nfc_cards,
        'has_fastag': bool(request.user.fastag_id)
    }
    return render(request, 'payment/methods.html', context)

@login_required
def add_nfc_card(request):
    if request.method == 'POST':
        card_id = request.POST.get('card_id')
        nickname = request.POST.get('nickname')
        
        if not card_id:
            messages.error(request, 'Card ID is required')
            return redirect('payment_methods')
        
        # Create NFC card
        NFCCard.objects.create(
            user=request.user,
            card_id=card_id,
            nickname=nickname,
            is_active=True
        )
        
        messages.success(request, 'NFC card added successfully')
    
    return redirect('payment_methods')

@login_required
def register_fastag(request):
    if request.method == 'POST':
        fastag_id = request.POST.get('fastag_id')
        vehicle_number = request.POST.get('vehicle_number')
        
        if not fastag_id or not vehicle_number:
            messages.error(request, 'Both FASTag ID and vehicle number are required')
            return redirect('payment_methods')
        
        # Update user
        request.user.fastag_id = fastag_id
        request.user.vehicle_number = vehicle_number
        request.user.save()
        
        messages.success(request, 'FASTag registered successfully')
    
    return redirect('payment_methods')

# API Views (unchanged from original)
class WalletTransactionListView(generics.ListAPIView):
    serializer_class = WalletTransactionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return WalletTransaction.objects.filter(user=self.request.user)

class AddFundsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = AddFundsSerializer(data=request.data)
        if serializer.is_valid():
            amount = serializer.validated_data['amount']
            payment_method = serializer.validated_data['payment_method']
            
            # In a real implementation, you would integrate with a payment gateway here
            # For demo purposes, we'll simulate a successful payment
            
            # Create transaction record
            transaction = WalletTransaction.objects.create(
                user=request.user,
                amount=amount,
                transaction_type='DEPOSIT',
                transaction_id=f"WALLET{int(time.time())}",
                status='SUCCESS',
                description=f"Wallet top-up via {payment_method}"
            )
            
            # Update user wallet balance
            request.user.wallet_balance += amount
            request.user.save()
            
            return Response(
                WalletTransactionSerializer(transaction).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class NFCCardListView(generics.ListCreateAPIView):
    serializer_class = NFCCardSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return NFCCard.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class RegisterFASTagView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = FASTagRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            fastag_id = serializer.validated_data['fastag_id']
            vehicle_number = serializer.validated_data['vehicle_number']
            
            # Update user profile
            request.user.fastag_id = fastag_id
            request.user.vehicle_number = vehicle_number
            request.user.save()
            
            return Response(
                {'message': 'FASTag registered successfully.'},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProcessPaymentView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        amount = request.data.get('amount')
        payment_method = request.data.get('payment_method')
        
        if not amount or not payment_method:
            return Response(
                {'error': 'Amount and payment method are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            amount = float(amount)
        except ValueError:
            return Response(
                {'error': 'Invalid amount.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if payment_method == 'WALLET':
            if request.user.wallet_balance >= amount:
                # Deduct from wallet
                request.user.wallet_balance -= amount
                request.user.save()
                
                # Record transaction
                transaction = WalletTransaction.objects.create(
                    user=request.user,
                    amount=amount,
                    transaction_type='PAYMENT',
                    transaction_id=f"PAY{int(time.time())}",
                    status='SUCCESS',
                    description='Parking payment'
                )
                
                return Response(
                    {'message': 'Payment successful.', 'transaction': WalletTransactionSerializer(transaction).data},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {'error': 'Insufficient wallet balance.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        elif payment_method == 'FASTAG':
            if not request.user.fastag_id:
                return Response(
                    {'error': 'No FASTag registered for this user.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Process FASTag payment
            from parking.services import FASTagPaymentService
            success = FASTagPaymentService.process_payment(request.user.fastag_id, amount)
            
            if success:
                return Response(
                    {'message': 'FASTag payment successful.'},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {'error': 'FASTag payment failed.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        elif payment_method == 'NFC':
            if not hasattr(request.user, 'nfc_cards') or not request.user.nfc_cards.filter(is_active=True).exists():
                return Response(
                    {'error': 'No active NFC card registered for this user.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get the most recently used NFC card
            nfc_card = request.user.nfc_cards.filter(is_active=True).order_by('-last_used').first()
            
            # Process NFC payment
            from parking.services import NFCPaymentService
            success = NFCPaymentService.process_payment(nfc_card.card_id, amount)
            
            if success:
                # Update last used time
                nfc_card.last_used = timezone.now()
                nfc_card.save()
                
                return Response(
                    {'message': 'NFC payment successful.'},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {'error': 'NFC payment failed.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        else:
            return Response(
                {'error': 'Invalid payment method.'},
                status=status.HTTP_400_BAD_REQUEST
            )