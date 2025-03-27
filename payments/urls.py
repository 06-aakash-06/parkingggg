from django.urls import path
from .views import (
    WalletTransactionListView,
    AddFundsView,
    NFCCardListView,
    RegisterFASTagView,
    ProcessPaymentView
)

urlpatterns = [
    # API Endpoints
    path('wallet/transactions/', WalletTransactionListView.as_view(), name='api-wallet-transactions'),
    path('wallet/add-funds/', AddFundsView.as_view(), name='api-add-funds'),
    path('nfc-cards/', NFCCardListView.as_view(), name='api-nfc-cards'),
    path('fastag/register/', RegisterFASTagView.as_view(), name='api-register-fastag'),
    path('process-payment/', ProcessPaymentView.as_view(), name='api-process-payment'),
]