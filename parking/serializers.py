from rest_framework import serializers

from .models import (
    ParkingSpace, 
    ParkingSpot, 
    ParkingImage, 
    ParkingReview,
    ParkingReservation,
    ParkingTransaction,
    ParkingOwnerEarning
)
from users.serializers import UserSerializer

class ParkingImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingImage
        fields = '__all__'

class ParkingSpotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingSpot
        fields = '__all__'

class ParkingSpaceSerializer(serializers.ModelSerializer):
    images = ParkingImageSerializer(many=True, read_only=True)
    spots = ParkingSpotSerializer(many=True, read_only=True)
    owner = UserSerializer(read_only=True)
    average_rating = serializers.SerializerMethodField()
    
    class Meta:
        model = ParkingSpace
        fields = '__all__'
    
    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if reviews:
            return sum([review.rating for review in reviews]) / len(reviews)
        return 0

class ParkingReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = ParkingReview
        fields = '__all__'
        read_only_fields = ('user', 'created_at')

class ParkingReservationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    parking_spot = ParkingSpotSerializer(read_only=True)
    parking_space = serializers.SerializerMethodField()
    
    class Meta:
        model = ParkingReservation
        fields = '__all__'
        read_only_fields = ('user', 'total_price', 'status', 'created_at', 'updated_at')
    
    def get_parking_space(self, obj):
        return ParkingSpaceSerializer(obj.parking_spot.parking_space).data

class CreateParkingReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingReservation
        fields = ('parking_spot', 'start_time', 'end_time', 'is_ev_charging')
    
    def validate(self, data):
        # Add validation logic here
        return data

class ParkingTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingTransaction
        fields = '__all__'

class ParkingOwnerEarningSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingOwnerEarning
        fields = '__all__'