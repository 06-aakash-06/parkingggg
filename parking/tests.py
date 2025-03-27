from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from datetime import datetime, timedelta
from .models import ParkingSpace, ParkingSpot, ParkingReservation

User = get_user_model()

class ParkingModelTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email='owner@example.com',
            password='testpass123',
            phone='+1234567890',
            user_type='PARKING_OWNER'
        )
        self.customer = User.objects.create_user(
            email='customer@example.com',
            password='testpass123',
            phone='+1987654321',
            user_type='CUSTOMER'
        )
        
        self.parking_space = ParkingSpace.objects.create(
            owner=self.owner,
            name='Downtown Parking',
            address='123 Main St',
            city='Metropolis',
            state='State',
            country='Country',
            pincode='123456',
            latitude=40.7128,
            longitude=-74.0060,
            total_spots=10,
            available_spots=10,
            price_per_hour=5.00,
            opening_time='08:00:00',
            closing_time='20:00:00',
            parking_type='PUBLIC',
            vehicle_type='CAR',
            is_verified=True
        )
        
        self.spot = ParkingSpot.objects.create(
            parking_space=self.parking_space,
            spot_number='A1',
            is_available=True,
            sensor_id='SENSOR001'
        )
    
    def test_create_parking_space(self):
        self.assertEqual(self.parking_space.name, 'Downtown Parking')
        self.assertEqual(self.parking_space.available_spots, 1)
    
    def test_create_reservation(self):
        start_time = datetime.now() + timedelta(hours=1)
        end_time = start_time + timedelta(hours=2)
        
        reservation = ParkingReservation.objects.create(
            user=self.customer,
            parking_spot=self.spot,
            start_time=start_time,
            end_time=end_time,
            total_price=10.00,
            status='CONFIRMED'
        )
        
        self.assertEqual(reservation.user, self.customer)
        self.assertEqual(reservation.parking_spot, self.spot)
        self.assertFalse(self.spot.is_available)  # Spot should be marked as unavailable

class ParkingViewsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.owner = User.objects.create_user(
            email='owner@example.com',
            password='testpass123',
            phone='+1234567890',
            user_type='PARKING_OWNER'
        )
        self.customer = User.objects.create_user(
            email='customer@example.com',
            password='testpass123',
            phone='+1987654321',
            user_type='CUSTOMER'
        )
        
        self.parking_space = ParkingSpace.objects.create(
            owner=self.owner,
            name='Downtown Parking',
            address='123 Main St',
            city='Metropolis',
            state='State',
            country='Country',
            pincode='123456',
            latitude=40.7128,
            longitude=-74.0060,
            total_spots=10,
            available_spots=10,
            price_per_hour=5.00,
            opening_time='08:00:00',
            closing_time='20:00:00',
            parking_type='PUBLIC',
            vehicle_type='CAR',
            is_verified=True
        )
        
        self.spot = ParkingSpot.objects.create(
            parking_space=self.parking_space,
            spot_number='A1',
            is_available=True,
            sensor_id='SENSOR001'
        )
        
        self.client.force_authenticate(user=self.customer)
    
    def test_list_parking_spaces(self):
        res = self.client.get('/api/parking/spaces/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
    
    def test_create_reservation(self):
        start_time = datetime.now() + timedelta(hours=1)
        end_time = start_time + timedelta(hours=2)
        
        payload = {
            'parking_spot': self.spot.id,
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat()
        }
        
        res = self.client.post('/api/parking/reservations/create/', payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['status'], 'CONFIRMED')