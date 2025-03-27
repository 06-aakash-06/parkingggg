from django.urls import path
from .views import (
    ParkingSpaceListView,
    ParkingSpaceDetailView,
    ParkingReviewListView,
    ParkingReservationListView,
    CreateParkingReservationView,
    CancelReservationView,
    ParkingOwnerEarningsView,
    VerifyParkingSpaceView,
    CheckInCheckOutView,
    parking_list,
    parking_detail,
    add_parking_space,
    parking_frontend_list
)

app_name = 'parking'

urlpatterns = [
    # API Endpoints
    path('spaces/', ParkingSpaceListView.as_view(), name='api-parking-space-list'),
    path('spaces/<int:id>/', ParkingSpaceDetailView.as_view(), name='api-parking-space-detail'),
    path('spaces/<int:parking_space_id>/reviews/', ParkingReviewListView.as_view(), name='api-parking-review-list'),
    path('reservations/', ParkingReservationListView.as_view(), name='api-reservation-list'),
    path('reservations/create/', CreateParkingReservationView.as_view(), name='api-create-reservation'),
    path('reservations/<int:reservation_id>/cancel/', CancelReservationView.as_view(), name='api-cancel-reservation'),
    path('reservations/<int:reservation_id>/check/', CheckInCheckOutView.as_view(), name='api-check-in-out'),
    path('owner/earnings/', ParkingOwnerEarningsView.as_view(), name='api-owner-earnings'),
    path('verify/<int:parking_space_id>/', VerifyParkingSpaceView.as_view(), name='api-verify-parking'),
    
    # Frontend Views
    path('', parking_list, name='list'),
    path('add/', add_parking_space, name='add'),
    path('<int:id>/', parking_detail, name='detail'),
    path('frontend/', parking_frontend_list, name='frontend-list'),
]