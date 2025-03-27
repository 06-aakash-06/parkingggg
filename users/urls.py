from django.urls import path
from .views import (
    UserRegistrationView,
    UserLoginView,
    UserProfileView,
    UserProfileUpdateView,
    LoyaltyProgramView
)

urlpatterns = [
    # API Endpoints
    path('register/', UserRegistrationView.as_view(), name='api-user-register'),
    path('login/', UserLoginView.as_view(), name='api-user-login'),
    path('profile/', UserProfileView.as_view(), name='api-user-profile'),
    path('profile/update/', UserProfileUpdateView.as_view(), name='api-user-profile-update'),
    path('loyalty/', LoyaltyProgramView.as_view(), name='api-user-loyalty'),
]