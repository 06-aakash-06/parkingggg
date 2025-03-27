from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('CUSTOMER', 'Customer'),
        ('PARKING_OWNER', 'Parking Owner'),
        ('ADMIN', 'Admin'),
        ('VERIFICATION_OFFICER', 'Verification Officer'),
    )
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',  # Changed from default 'user_set'
        blank=True,
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',  # Changed from default 'user_set'
        blank=True,
        verbose_name='user permissions'
    )

    
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='CUSTOMER')
    # In your User model (models.py)
    phone = models.CharField(max_length=15, blank=True, null=True)  
    is_verified = models.BooleanField(default=False)
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    nfc_card_id = models.CharField(max_length=100, blank=True, null=True)
    vehicle_number = models.CharField(max_length=20, blank=True, null=True)
    fastag_id = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return self.email

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=10, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.email}'s Profile"

class LoyaltyProgram(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='loyalty')
    points = models.IntegerField(default=0)
    level = models.IntegerField(default=1)
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.email} - Level {self.level}"