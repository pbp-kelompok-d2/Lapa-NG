from django.forms import ModelForm
from booking.models import Venue

class VenueForm(ModelForm):
    class Meta:
        model = Venue
        fields = ["name", "price", "description", "time", "capacity", "category", "thumbnail", "is_featured"]