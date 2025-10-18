from django import forms
from .models import Booking

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = [
            'venue_ref', 'venue_name', 'venue_city', 'sport_type',
            'date', 'start_time', 'end_time', 'notes'
        ]

    def clean(self):
        cleaned = super().clean()
        s, e = cleaned.get('start_time'), cleaned.get('end_time')
        if s and e and e <= s:
            raise forms.ValidationError("End time must be after start time.")
        # venue_name wajib biar UI tetap jelas meski belum ada FK
        if not cleaned.get('venue_name'):
            raise forms.ValidationError("Venue name is required.")
        return cleaned
