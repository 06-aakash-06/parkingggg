from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create UserProfile and LoyaltyProgram when a new User is created"""
    if created:
        from .models import UserProfile, LoyaltyProgram
        UserProfile.objects.create(user=instance)
        LoyaltyProgram.objects.create(user=instance)