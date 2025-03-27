from django.contrib import admin
from .models import (
    ParkingSpace, 
    ParkingSpot, 
    ParkingImage, 
    ParkingReview,
    ParkingReservation,
    ParkingTransaction,
    ParkingOwnerEarning
)

class ParkingImageInline(admin.TabularInline):
    model = ParkingImage
    extra = 1

class ParkingSpotInline(admin.TabularInline):
    model = ParkingSpot
    extra = 1

class ParkingReviewInline(admin.TabularInline):
    model = ParkingReview
    extra = 0
    readonly_fields = ('user', 'rating', 'comment', 'created_at')

class ParkingSpaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'parking_type', 'vehicle_type', 'price_per_hour', 'is_verified')
    list_filter = ('parking_type', 'vehicle_type', 'is_verified', 'city')
    search_fields = ('name', 'address', 'city', 'owner__email')
    raw_id_fields = ('owner', 'verification_officer')
    inlines = [ParkingImageInline, ParkingSpotInline, ParkingReviewInline]

class ParkingReservationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'parking_spot', 'start_time', 'end_time', 'status', 'total_price')
    list_filter = ('status', 'is_ev_charging', 'start_time')
    search_fields = ('user__email', 'parking_spot__parking_space__name')
    raw_id_fields = ('user', 'parking_spot')

class ParkingTransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'reservation', 'amount', 'payment_method', 'status')
    list_filter = ('status', 'payment_method')
    search_fields = ('transaction_id', 'reservation__user__email')

class ParkingOwnerEarningAdmin(admin.ModelAdmin):
    list_display = ('owner', 'reservation', 'amount', 'commission', 'net_amount', 'is_paid')
    list_filter = ('is_paid',)
    search_fields = ('owner__email', 'reservation__id')

admin.site.register(ParkingSpace, ParkingSpaceAdmin)
admin.site.register(ParkingReservation, ParkingReservationAdmin)
admin.site.register(ParkingTransaction, ParkingTransactionAdmin)
admin.site.register(ParkingOwnerEarning, ParkingOwnerEarningAdmin)
admin.site.register(ParkingReview)