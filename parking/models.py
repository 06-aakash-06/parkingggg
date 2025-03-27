from django.db import models
from users.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class ParkingSpace(models.Model):
    PARKING_TYPE_CHOICES = (
        ('PUBLIC', 'Public'),
        ('PRIVATE', 'Private'),
    )
    
    VEHICLE_TYPE_CHOICES = (
        ('CAR', 'Car'),
        ('BIKE', 'Bike'),
        ('BOTH', 'Both'),
    )
    
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='parking_spaces')
    name = models.CharField(max_length=255)
    description = models.TextField()
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    latitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6,
        validators=[
            MinValueValidator(-90),
            MaxValueValidator(90)
        ]
    )
    longitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6,
        validators=[
            MinValueValidator(-180),
            MaxValueValidator(180)
        ]
    )
    total_spots = models.PositiveIntegerField()
    available_spots = models.PositiveIntegerField()
    price_per_hour = models.DecimalField(
        max_digits=6, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    parking_type = models.CharField(max_length=10, choices=PARKING_TYPE_CHOICES)
    vehicle_type = models.CharField(max_length=10, choices=VEHICLE_TYPE_CHOICES)
    is_verified = models.BooleanField(default=False)
    verification_officer = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='verified_parkings'
    )
    verification_date = models.DateTimeField(null=True, blank=True)
    has_ev_charging = models.BooleanField(default=False)
    ev_charging_price = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0.01)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.city}"

class ParkingSpot(models.Model):
    parking_space = models.ForeignKey(
        ParkingSpace, 
        on_delete=models.CASCADE, 
        related_name='spots'
    )
    spot_number = models.CharField(max_length=10)
    is_available = models.BooleanField(default=True)
    is_ev_charging = models.BooleanField(default=False)
    image = models.ImageField(upload_to='parking_spots/', null=True, blank=True)
    sensor_id = models.CharField(max_length=100, unique=True)
    ev_charging_power = models.PositiveIntegerField(
        default=0, 
        help_text="Power in kW"
    )
    def __str__(self):
        return f"{self.location} - {self.spot_type}"
class Meta:
    indexes = [
        models.Index(fields=['is_available']),
    ]

    def __str__(self):
        return f"{self.parking_space.name} - Spot {self.spot_number}"

class ParkingImage(models.Model):
    parking_space = models.ForeignKey(
        ParkingSpace, 
        on_delete=models.CASCADE, 
        related_name='images'
    )
    image = models.ImageField(upload_to='parking_images/')
    is_featured = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Image for {self.parking_space.name}"

class ParkingReview(models.Model):
    parking_space = models.ForeignKey(
        ParkingSpace, 
        on_delete=models.CASCADE, 
        related_name='reviews'
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ]
    )
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.email}'s review for {self.parking_space.name}"

class ParkingReservation(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
        ('COMPLETED', 'Completed'),
    )
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='reservations'
    )
    parking_spot = models.ForeignKey(
        ParkingSpot, 
        on_delete=models.CASCADE, 
        related_name='reservations'
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES, 
        default='PENDING'
    )
    total_price = models.DecimalField(
        max_digits=8, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    is_ev_charging = models.BooleanField(default=False)
    ev_charging_time = models.PositiveIntegerField(null=True, blank=True)  # in minutes
    ev_charging_cost = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0.01)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Reservation #{self.id} - {self.user.email}"

class ParkingTransaction(models.Model):
    reservation = models.OneToOneField(
        ParkingReservation, 
        on_delete=models.CASCADE, 
        related_name='transaction'
    )
    amount = models.DecimalField(
        max_digits=8, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    payment_method = models.CharField(max_length=20)  # FASTag, NFC, Wallet, etc.
    transaction_id = models.CharField(max_length=100)
    status = models.CharField(max_length=20)  # SUCCESS, FAILED, PENDING
    payment_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Transaction #{self.transaction_id}"

class ParkingOwnerEarning(models.Model):
    owner = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='earnings'
    )
    reservation = models.ForeignKey(
        ParkingReservation, 
        on_delete=models.CASCADE
    )
    amount = models.DecimalField(
        max_digits=8, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    commission = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[MinValueValidator(0.00)]
    )
    net_amount = models.DecimalField(
        max_digits=8, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    payment_date = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Earning for {self.owner.email} - {self.reservation.id}"