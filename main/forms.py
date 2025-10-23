from django import forms
from .models import Venue

class VenueForm(forms.ModelForm):
    class Meta:
        model = Venue
        
        # ------ THE fields LIST ------
        fields = [
            'name', 
            'category', 
            'description', 
            'address', 
            'price', 
            'capacity', 
            'opening_time', 
            'closing_time',
            'thumbnail',
            'is_featured'
        ]
        # ----------------------------

        # ------  Attributes  ------
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'e.g., LapaNG Futsal Center'
            }),
            'description': forms.Textarea(attrs={
                'rows': 3, 
                'placeholder': 'Tell users about your venue, the facilities, floor type, etc.'
            }),
            'address': forms.TextInput(attrs={  
                'placeholder': 'e.g., Jl. Margonda Raya No. 100, Depok'
            }),
            'price': forms.NumberInput(attrs={
                'placeholder': '50000'
            }),
            'capacity': forms.NumberInput(attrs={
                'placeholder': '10'
            }),
            'opening_time': forms.TimeInput(attrs={
                'type': 'time'  # This gives you the "clock" picker
            }),
            'closing_time': forms.TimeInput(attrs={
                'type': 'time'  # This gives you the "clock" picker
            }),
            'thumbnail': forms.TextInput(attrs={
                'placeholder': 'e.g., my_venue.jpg or https://...'
            }),
        }
