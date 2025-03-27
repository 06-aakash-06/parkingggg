from django import forms
from .models import ParkingSpace, ParkingSpot, ParkingImage

class ParkingSpaceForm(forms.ModelForm):
    class Meta:
        model = ParkingSpace
        fields = [
            'name', 'description', 'address', 'city', 'state', 'country', 'pincode',
            'latitude', 'longitude', 'total_spots', 'price_per_hour', 'opening_time',
            'closing_time', 'parking_type', 'vehicle_type', 'has_ev_charging', 
            'ev_charging_price'
        ]
        widgets = {
            'opening_time': forms.TimeInput(attrs={'type': 'time'}),
            'closing_time': forms.TimeInput(attrs={'type': 'time'}),
        }

class ParkingSpotForm(forms.ModelForm):
    class Meta:
        model = ParkingSpot
        fields = ['spot_number', 'is_ev_charging', 'image', 'sensor_id', 'ev_charging_power']

class ParkingImageForm(forms.ModelForm):
    class Meta:
        model = ParkingImage
        fields = ['image', 'is_featured']