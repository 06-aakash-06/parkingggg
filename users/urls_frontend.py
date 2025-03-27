from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Profile
    path('', views.profile_view, name='profile'),
    path('change-password/', views.change_password, name='change_password'),
]