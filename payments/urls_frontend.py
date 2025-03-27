from django.urls import path
from . import views

urlpatterns = [
    path('', views.wallet, name='wallet'),
    path('add-funds/', views.add_funds, name='add_funds'),
    path('methods/', views.payment_methods, name='payment_methods'),
    path('methods/nfc/add/', views.add_nfc_card, name='add_nfc_card'),
    path('methods/fastag/register/', views.register_fastag, name='register_fastag'),
]