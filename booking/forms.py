from django import forms
from .models import Booking

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['borrower_name', 'booking_date', 'start_time', 'end_time']
        widgets = {
            'booking_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        }
        labels = {
            'borrower_name': 'Nama Peminjam',
            'booking_date': 'Tanggal Booking',
            'start_time': 'Jam Mulai',
            'end_time': 'Jam Selesai',
        }
