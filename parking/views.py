from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from rest_framework import generics, status, permissions, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import render, redirect
from django.contrib import messages
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from .models import (
    ParkingSpace, 
    ParkingSpot, 
    ParkingReservation,
    ParkingReview,
    ParkingOwnerEarning
)
from .serializers import (
    ParkingSpaceSerializer,
    ParkingReviewSerializer,
    ParkingReservationSerializer,
    CreateParkingReservationSerializer,
    ParkingOwnerEarningSerializer
)
from users.models import User
import datetime
from django.utils import timezone
from django.db.models import Q
from .forms import ParkingSpaceForm
# Template Views
def add_parking_space(request):
    if request.method == 'POST':
        form = ParkingSpaceForm(request.POST)
        if form.is_valid():
            parking_space = form.save(commit=False)
            parking_space.owner = request.user
            parking_space.save()
            messages.success(request, 'Parking space added successfully!')
            return redirect('parking:list')  # Update with your actual list view name
    else:
        form = ParkingSpaceForm()
    return render(request, 'parking/add_space.html', {'form': form})
def home(request):
    return render(request, 'home.html')

@login_required
def parking_list(request):
    queryset = ParkingSpace.objects.filter(is_verified=True)
    
    # Handle location filtering
    lat = request.GET.get('lat')
    lng = request.GET.get('lng')
    radius = request.GET.get('radius', 10)  # default 10 km
    
    if lat and lng:
        user_location = Point(float(lng), float(lat), srid=4326)
        queryset = queryset.annotate(
            distance=Distance('location', user_location)
        ).filter(distance__lte=radius * 1000)  # Convert km to meters
        default_lat, default_lng = float(lat), float(lng)
    else:
        # Default to New York if no location provided
        default_lat, default_lng = 40.7128, -74.0060
    
    # Handle other filters
    vehicle_type = request.GET.get('vehicle_type')
    if vehicle_type:
        queryset = queryset.filter(vehicle_type=vehicle_type)
    
    price_range = request.GET.get('price_range')
    if price_range:
        if price_range == '0-50':
            queryset = queryset.filter(price_per_hour__lte=50)
        elif price_range == '50-100':
            queryset = queryset.filter(price_per_hour__gt=50, price_per_hour__lte=100)
        elif price_range == '100+':
            queryset = queryset.filter(price_per_hour__gt=100)
    
    # Pagination
    paginator = Paginator(queryset, 10)  # Show 10 parkings per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'parkings': page_obj,
        'default_lat': default_lat,
        'default_lng': default_lng,
    }
    return render(request, 'parking/list.html', context)

@login_required
def parking_detail(request, id):
    parking = get_object_or_404(ParkingSpace, id=id)
    user_has_booked = ParkingReservation.objects.filter(
        user=request.user,
        parking_spot__parking_space=parking
    ).exists()
    
    reviews = ParkingReview.objects.filter(parking_space=parking)
    
    context = {
        'parking': parking,
        'reviews': reviews,
        'user_has_booked': user_has_booked,
    }
    return render(request, 'parking/detail.html', context)

@login_required
def create_booking(request, parking_space_id):
    if request.method == 'POST':
        parking_space = get_object_or_404(ParkingSpace, id=parking_space_id)
        parking_spot = parking_space.parking_spots.filter(is_available=True).first()
        
        if not parking_spot:
            messages.error(request, 'No available spots in this parking space')
            return redirect('parking_detail', id=parking_space_id)
        
        try:
            start_time = datetime.datetime.strptime(
                request.POST.get('start_time'),
                '%Y-%m-%dT%H:%M'
            )
            end_time = datetime.datetime.strptime(
                request.POST.get('end_time'),
                '%Y-%m-%dT%H:%M'
            )
            vehicle_number = request.POST.get('vehicle_number')
            is_ev_charging = request.POST.get('is_ev_charging') == 'on'
            
            # Check for overlapping reservations
            overlapping = ParkingReservation.objects.filter(
                parking_spot=parking_spot,
                status='CONFIRMED',
                start_time__lt=end_time,
                end_time__gt=start_time
            ).exists()
            
            if overlapping:
                messages.error(request, 'This spot is already booked for the selected time')
                return redirect('parking_detail', id=parking_space_id)
            
            # Calculate price
            duration = (end_time - start_time).total_seconds() / 3600
            total_price = duration * parking_space.price_per_hour
            
            # Create reservation
            reservation = ParkingReservation.objects.create(
                user=request.user,
                parking_spot=parking_spot,
                start_time=start_time,
                end_time=end_time,
                vehicle_number=vehicle_number,
                total_price=total_price,
                is_ev_charging=is_ev_charging,
                status='CONFIRMED'
            )
            
            # Mark spot as unavailable
            parking_spot.is_available = False
            parking_spot.save()
            
            messages.success(request, 'Booking created successfully!')
            return redirect('booking_detail', reservation_id=reservation.id)
        
        except Exception as e:
            messages.error(request, f'Error creating booking: {str(e)}')
            return redirect('parking_detail', id=parking_space_id)
    
    return redirect('parking_detail', id=parking_space_id)

@login_required
def my_bookings(request):
    bookings = ParkingReservation.objects.filter(user=request.user).order_by('-created_at')
    
    # Categorize bookings
    upcoming = bookings.filter(
        status='CONFIRMED',
        end_time__gt=timezone.now()
    )
    past = bookings.filter(
        Q(status='COMPLETED') | Q(status='CONFIRMED', end_time__lte=timezone.now())
    )
    cancelled = bookings.filter(status='CANCELLED')
    
    context = {
        'upcoming_bookings': upcoming,
        'past_bookings': past,
        'cancelled_bookings': cancelled,
    }
    return render(request, 'bookings/my_bookings.html', context)

@login_required
def booking_detail(request, reservation_id):
    booking = get_object_or_404(ParkingReservation, id=reservation_id, user=request.user)
    context = {'booking': booking}
    return render(request, 'bookings/detail.html', context)

@login_required
def cancel_booking(request, reservation_id):
    booking = get_object_or_404(ParkingReservation, id=reservation_id, user=request.user)
    
    if request.method == 'POST':
        if booking.start_time > timezone.now():
            booking.status = 'CANCELLED'
            booking.cancellation_reason = request.POST.get('cancellation_reason', '')
            booking.save()
            
            # Mark spot as available
            booking.parking_spot.is_available = True
            booking.parking_spot.save()
            
            messages.success(request, 'Booking cancelled successfully')
            return redirect('my_bookings')
        else:
            messages.error(request, 'Cannot cancel booking after it has started')
    
    return redirect('booking_detail', reservation_id=reservation_id)

@login_required
def add_review(request, parking_space_id):
    if request.method == 'POST':
        parking_space = get_object_or_404(ParkingSpace, id=parking_space_id)
        rating = int(request.POST.get('rating'))
        comment = request.POST.get('comment')
        
        # Check if user has booked this parking space
        has_booked = ParkingReservation.objects.filter(
            user=request.user,
            parking_spot__parking_space=parking_space,
            status='COMPLETED'
        ).exists()
        
        if not has_booked:
            messages.error(request, 'You need to complete a booking before leaving a review')
            return redirect('parking_detail', id=parking_space_id)
        
        # Create review
        ParkingReview.objects.create(
            user=request.user,
            parking_space=parking_space,
            rating=rating,
            comment=comment
        )
        
        messages.success(request, 'Review submitted successfully!')
    
    return redirect('parking_detail', id=parking_space_id)
def parking_space_list(request):
    """Alternative to parking_frontend_list"""
    parkings = ParkingSpace.objects.all()
    return render(request, 'parking/list.html', {'parkings': parkings})
# API Views (unchanged from original)
class ParkingSpaceListView(generics.ListAPIView):
    serializer_class = ParkingSpaceSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['parking_type', 'vehicle_type', 'has_ev_charging', 'city']
    search_fields = ['name', 'address', 'city', 'state']
    ordering_fields = ['price_per_hour', 'available_spots']
    
    def get_queryset(self):
        queryset = ParkingSpace.objects.filter(is_verified=True)
        
        lat = self.request.query_params.get('lat')
        lng = self.request.query_params.get('lng')
        radius = self.request.query_params.get('radius', 10)
        
        if lat and lng:
            user_location = Point(float(lng), float(lat), srid=4326)
            queryset = queryset.annotate(
                distance=Distance('location', user_location)
            ).filter(distance__lte=radius * 1000)
        
        return queryset

class ParkingSpaceDetailView(generics.RetrieveAPIView):
    queryset = ParkingSpace.objects.all()
    serializer_class = ParkingSpaceSerializer
    lookup_field = 'id'

class ParkingReviewListView(generics.ListCreateAPIView):
    serializer_class = ParkingReviewSerializer
    
    def get_queryset(self):
        parking_space_id = self.kwargs.get('parking_space_id')
        return ParkingReview.objects.filter(parking_space_id=parking_space_id)
    
    def perform_create(self, serializer):
        parking_space_id = self.kwargs.get('parking_space_id')
        serializer.save(
            user=self.request.user,
            parking_space_id=parking_space_id
        )

class ParkingReservationListView(generics.ListAPIView):
    serializer_class = ParkingReservationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ParkingReservation.objects.filter(user=self.request.user)

class CreateParkingReservationView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = CreateParkingReservationSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            # Check spot availability
            parking_spot = serializer.validated_data['parking_spot']
            start_time = serializer.validated_data['start_time']
            end_time = serializer.validated_data['end_time']
            
            # Check if spot is already reserved for the given time
            overlapping_reservations = ParkingReservation.objects.filter(
                parking_spot=parking_spot,
                status='CONFIRMED',
                start_time__lt=end_time,
                end_time__gt=start_time
            )
            
            if overlapping_reservations.exists():
                return Response(
                    {'error': 'This spot is already reserved for the selected time.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Calculate price
            duration_hours = (end_time - start_time).total_seconds() / 3600
            total_price = duration_hours * parking_spot.parking_space.price_per_hour
            
            # EV charging cost if applicable
            ev_charging_cost = 0
            if serializer.validated_data['is_ev_charging'] and parking_spot.parking_space.has_ev_charging:
                ev_charging_time = duration_hours * 60  # convert to minutes
                ev_charging_cost = ev_charging_time * parking_spot.parking_space.ev_charging_price / 60
                total_price += ev_charging_cost
            
            # Create reservation
            reservation = ParkingReservation.objects.create(
                user=request.user,
                parking_spot=parking_spot,
                start_time=start_time,
                end_time=end_time,
                total_price=total_price,
                is_ev_charging=serializer.validated_data['is_ev_charging'],
                ev_charging_time=ev_charging_time if serializer.validated_data['is_ev_charging'] else None,
                ev_charging_cost=ev_charging_cost if serializer.validated_data['is_ev_charging'] else None,
                status='CONFIRMED'
            )
            
            # Update spot availability if needed
            if parking_spot.is_available:
                parking_spot.is_available = False
                parking_spot.save()
            
            return Response(
                ParkingReservationSerializer(reservation).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ParkingSpaceListView(generics.ListCreateAPIView):
    queryset = ParkingSpace.objects.all()
    serializer_class = ParkingSpaceSerializer

class ParkingSpaceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ParkingSpace.objects.all()
    serializer_class = ParkingSpaceSerializer

# Frontend Views
def parking_frontend_list(request):
    parkings = ParkingSpace.objects.all()
    return render(request, 'parking/list.html', {'parkings': parkings})

class CancelReservationView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, reservation_id):
        try:
            reservation = ParkingReservation.objects.get(id=reservation_id, user=request.user)
            
            # Only allow cancellation if reservation hasn't started yet
            if reservation.start_time > timezone.now():
                reservation.status = 'CANCELLED'
                reservation.save()
                
                # Mark spot as available
                reservation.parking_spot.is_available = True
                reservation.parking_spot.save()
                
                # TODO: Process refund if payment was made
                
                return Response(
                    {'message': 'Reservation cancelled successfully.'},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {'error': 'Cannot cancel reservation after it has started.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except ParkingReservation.DoesNotExist:
            return Response(
                {'error': 'Reservation not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

class ParkingOwnerEarningsView(generics.ListAPIView):
    serializer_class = ParkingOwnerEarningSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ParkingOwnerEarning.objects.filter(owner=self.request.user)

class VerifyParkingSpaceView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, parking_space_id):
        if request.user.user_type != 'VERIFICATION_OFFICER':
            return Response(
                {'error': 'Only verification officers can verify parking spaces.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            parking_space = ParkingSpace.objects.get(id=parking_space_id)
            
            if parking_space.is_verified:
                return Response(
                    {'error': 'Parking space is already verified.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            parking_space.is_verified = True
            parking_space.verification_officer = request.user
            parking_space.verification_date = timezone.now()
            parking_space.save()
            
            return Response(
                {'message': 'Parking space verified successfully.'},
                status=status.HTTP_200_OK
            )
        except ParkingSpace.DoesNotExist:
            return Response(
                {'error': 'Parking space not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

class CheckInCheckOutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, reservation_id):
        action = request.data.get('action')  # 'check_in' or 'check_out'
        
        try:
            reservation = ParkingReservation.objects.get(id=reservation_id)
            
            if action == 'check_in':
                # Verify reservation belongs to user or user is parking owner
                if reservation.user != request.user and reservation.parking_spot.parking_space.owner != request.user:
                    return Response(
                        {'error': 'You are not authorized to perform this action.'},
                        status=status.HTTP_403_FORBIDDEN
                    )
                
                # Update reservation status or other check-in logic
                # ...
                
                return Response(
                    {'message': 'Checked in successfully.'},
                    status=status.HTTP_200_OK
                )
            
            elif action == 'check_out':
                # Verify reservation belongs to user or user is parking owner
                if reservation.user != request.user and reservation.parking_spot.parking_space.owner != request.user:
                    return Response(
                        {'error': 'You are not authorized to perform this action.'},
                        status=status.HTTP_403_FORBIDDEN
                    )
                
                # Process payment if not already done
                if not hasattr(reservation, 'transaction'):
                    # Calculate actual duration and adjust price
                    actual_end_time = timezone.now()
                    actual_duration = (actual_end_time - reservation.start_time).total_seconds() / 3600
                    actual_price = actual_duration * reservation.parking_spot.parking_space.price_per_hour
                    
                    # Process payment (simplified)
                    payment_success = self.process_payment(reservation.user, actual_price)
                    
                    if payment_success:
                        # Create transaction record
                        ParkingTransaction.objects.create(
                            reservation=reservation,
                            amount=actual_price,
                            payment_method='FASTAG',  # or other method
                            transaction_id=f"TXN{timezone.now().timestamp()}",
                            status='SUCCESS'
                        )
                        
                        # Calculate owner earnings
                        commission = actual_price * 0.15  # 15% commission
                        net_amount = actual_price - commission
                        
                        ParkingOwnerEarning.objects.create(
                            owner=reservation.parking_spot.parking_space.owner,
                            reservation=reservation,
                            amount=actual_price,
                            commission=commission,
                            net_amount=net_amount
                        )
                        
                        # Update reservation
                        reservation.end_time = actual_end_time
                        reservation.total_price = actual_price
                        reservation.status = 'COMPLETED'
                        reservation.save()
                        
                        # Mark spot as available
                        reservation.parking_spot.is_available = True
                        reservation.parking_spot.save()
                        
                        # Add loyalty points
                        self.add_loyalty_points(reservation.user, actual_price)
                        
                        return Response(
                            {'message': 'Checked out successfully. Payment processed.'},
                            status=status.HTTP_200_OK
                        )
                    else:
                        return Response(
                            {'error': 'Payment failed. Please try again.'},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                else:
                    return Response(
                        {'message': 'Already checked out.'},
                        status=status.HTTP_200_OK
                    )
            
            else:
                return Response(
                    {'error': 'Invalid action.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except ParkingReservation.DoesNotExist:
            return Response(
                {'error': 'Reservation not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    def process_payment(self, user, amount):
        # Simplified payment processing
        # In real implementation, integrate with FASTag or NFC payment gateway
        return True
    
    def add_loyalty_points(self, user, amount):
        # Add 1 point for every 100 rupees spent
        points = int(amount / 100)
        loyalty = user.loyalty
        loyalty.points += points
        loyalty.level = min(5, 1 + (loyalty.points // 100))  # 5 levels max
        loyalty.save()