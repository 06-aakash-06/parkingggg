from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import ParkingSpace, ParkingReservation, ParkingSpot

@receiver(post_save, sender=ParkingSpace)
def update_available_spots(sender, instance, created, **kwargs):
    """
    Update available_spots count when spots are added or removed
    """
    if not created:
        total_spots = instance.spots.count()
        if instance.total_spots != total_spots:
            instance.total_spots = total_spots
            instance.save(update_fields=['total_spots'])
    
    # Update available_spots count
    available = instance.spots.filter(is_available=True).count()
    if instance.available_spots != available:
        instance.available_spots = available
        instance.save(update_fields=['available_spots'])

@receiver(post_save, sender=ParkingSpot)
def update_parking_space_availability(sender, instance, created, **kwargs):
    """
    Update parent parking space's available_spots when a spot's availability changes
    """
    parking_space = instance.parking_space
    available = parking_space.spots.filter(is_available=True).count()
    if parking_space.available_spots != available:
        parking_space.available_spots = available
        parking_space.save(update_fields=['available_spots'])

@receiver(pre_save, sender=ParkingReservation)
def validate_reservation(sender, instance, **kwargs):
    """
    Validate reservation before saving
    """
    if instance.pk is None:  # New reservation
        # Check if spot is available for the requested time
        overlapping = ParkingReservation.objects.filter(
            parking_spot=instance.parking_spot,
            status='CONFIRMED',
            start_time__lt=instance.end_time,
            end_time__gt=instance.start_time
        ).exists()
        
        if overlapping:
            raise ValueError("This spot is already reserved for the selected time.")