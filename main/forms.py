from django import forms
from .models import Venue

class VenueForm(forms.ModelForm):
    class Meta:
        model = Venue
        # These are the fields the user will fill out
        fields = [
            'name', 
            'category', 
            'address', 
            'price', 
            'capacity', 
            'opening_time', 
            'closing_time',
            'time_display',
            'thumbnail'
        ]
