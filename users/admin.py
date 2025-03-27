from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserProfile, LoyaltyProgram

class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'phone', 'user_type', 'is_verified', 'is_staff')
    list_filter = ('user_type', 'is_verified', 'is_staff', 'is_superuser')
    search_fields = ('email', 'first_name', 'last_name', 'phone')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Custom Fields', {'fields': ('user_type', 'is_verified', 'wallet_balance', 'nfc_card_id', 'vehicle_number', 'fastag_id')}),
    )

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'city', 'state', 'country')
    search_fields = ('user__email', 'city', 'state', 'country')
    raw_id_fields = ('user',)

class LoyaltyProgramAdmin(admin.ModelAdmin):
    list_display = ('user', 'points', 'level', 'last_updated')
    search_fields = ('user__email',)
    raw_id_fields = ('user',)

admin.site.register(User, CustomUserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(LoyaltyProgram, LoyaltyProgramAdmin)