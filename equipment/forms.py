from django.forms import ModelForm
from .models import Equipment

class EquipmentForm(ModelForm):
    class Meta:
        model = Equipment
        fields = [
            'name',
            'price_per_hour',
            'sport_category',
            'region',
            'quantity',
            'available',
            'thumbnail',
        ]