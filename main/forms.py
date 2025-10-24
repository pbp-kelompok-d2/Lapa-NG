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
        # ------  Attributes  ------
        
        # Definisikan class styling-nya sekali saja
        

        input_classes = 'w-full px-4 py-3 border border-gray-400 rounded-md focus:outline-none focus:border-green-500 transition-colors bg-white'

        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'e.g., LapaNG Futsal Center',
                'class': input_classes
            }),
            
            # Kita HARUS menambahkan 'category' di sini agar ikut di-style
            'category': forms.Select(attrs={
                'class': input_classes
            }),

            'description': forms.Textarea(attrs={
                'rows': 3, 
                'placeholder': 'Tell users about your venue, the facilities, floor type, etc.',
                'class': input_classes
            }),
            'address': forms.TextInput(attrs={  
                'placeholder': 'e.g., Jl. Margonda Raya No. 100, Depok',
                'class': input_classes
            }),
            'price': forms.NumberInput(attrs={
                'placeholder': '50000',
                'class': input_classes
            }),
            'capacity': forms.NumberInput(attrs={
                'placeholder': '10',
                'class': input_classes
            }),
            'opening_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': input_classes
            }),
            'closing_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': input_classes
            }),
            'thumbnail': forms.TextInput(attrs={
                'placeholder': 'e.g., my_venue.jpg or https://...',
                'class': input_classes
            }),
        }
