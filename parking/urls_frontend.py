from django.urls import path
from . import views

urlpatterns = [
    # Parking Views
    path('', views.parking_list, name='parking_list'),
    path('<int:id>/', views.parking_detail, name='parking_detail'),
    path('<int:parking_space_id>/book/', views.create_booking, name='create_booking'),
    path('<int:parking_space_id>/review/', views.add_review, name='add_review'),
    
    # Booking Views
    path('my/', views.my_bookings, name='my_bookings'),
    path('my/<int:reservation_id>/', views.booking_detail, name='booking_detail'),
    path('my/<int:reservation_id>/cancel/', views.cancel_booking, name='cancel_booking'),
]