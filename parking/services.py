import requests
from django.conf import settings
from django.utils import timezone
from .models import ParkingSpot

class SensorService:
    @staticmethod
    def update_spot_availability(sensor_id, is_occupied):
        try:
            spot = ParkingSpot.objects.get(sensor_id=sensor_id)
            spot.is_available = not is_occupied
            spot.save()
            return True
        except ParkingSpot.DoesNotExist:
            return False

class FASTagPaymentService:
    @staticmethod
    def process_payment(fastag_id, amount):
        # This is a mock implementation
        # In a real system, you would call the FASTag API
        headers = {
            'Authorization': f'Bearer {settings.FASTAG_API_KEY}',
            'Content-Type': 'application/json'
        }
        payload = {
            'fastag_id': fastag_id,
            'amount': amount,
            'merchant_id': 'SMART_PARKING'
        }
        
        try:
            # Mock response - in real implementation, make actual API call
            # response = requests.post(settings.FASTAG_API_URL, json=payload, headers=headers)
            # return response.status_code == 200
            
            # For demo purposes, always return True
            return True
        except Exception as e:
            print(f"FASTag payment error: {e}")
            return False

class NFCPaymentService:
    @staticmethod
    def process_payment(nfc_card_id, amount):
        # This is a mock implementation
        # In a real system, you would call the NFC payment gateway
        headers = {
            'Authorization': f'Bearer {settings.NFC_SECRET_KEY}',
            'Content-Type': 'application/json'
        }
        payload = {
            'card_id': nfc_card_id,
            'amount': amount,
            'merchant_id': settings.NFC_MERCHANT_ID
        }
        
        try:
            # Mock response - in real implementation, make actual API call
            # response = requests.post('https://api.nfc-payment.com/charge', json=payload, headers=headers)
            # return response.status_code == 200
            
            # For demo purposes, always return True
            return True
        except Exception as e:
            print(f"NFC payment error: {e}")
            return False

class ParkingAvailabilityService:
    @staticmethod
    def get_nearby_available_spots(latitude, longitude, radius=5, vehicle_type='CAR'):
        """
        Find available parking spots within a given radius
        """
        user_location = Point(float(longitude), float(latitude), srid=4326)
        
        queryset = ParkingSpot.objects.filter(
            is_available=True,
            parking_space__location__distance_lte=(user_location, radius * 1000)
        )
        
        if vehicle_type == 'CAR':
            queryset = queryset.filter(parking_space__vehicle_type__in=['CAR', 'BOTH'])
        elif vehicle_type == 'BIKE':
            queryset = queryset.filter(parking_space__vehicle_type__in=['BIKE', 'BOTH'])
        
        return queryset.annotate(
            distance=Distance('parking_space__location', user_location)
        ).order_by('distance')

class ReservationService:
    @staticmethod
    def check_spot_availability(spot_id, start_time, end_time):
        """
        Check if a spot is available for the given time range
        """
        overlapping_reservations = ParkingReservation.objects.filter(
            parking_spot_id=spot_id,
            status='CONFIRMED',
            start_time__lt=end_time,
            end_time__gt=start_time
        )
        return not overlapping_reservations.exists()