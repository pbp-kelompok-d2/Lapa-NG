import uuid
from django.db import models
from django.utils import timezone
from django.conf import settings

class Equipment(models.Model):
    # Pilihan kategori olahraga
    SPORT_CHOICES = [
        ('soccer', 'Soccer'),
        ('tennis', 'Tennis'),
        ('badminton', 'Badminton'),
        ('futsal', 'Futsal'),
        ('basket', 'Basket'),
        ('multi', 'Multi-sport'),
    ]

    # Pilihan wilayah di Jakarta untuk filtering
    JAKARTA_REGION_CHOICES = [
        ('jakarta_pusat', 'Jakarta Pusat'),
        ('jakarta_selatan', 'Jakarta Selatan'),
        ('jakarta_barat', 'Jakarta Barat'),
        ('jakarta_timur', 'Jakarta Timur'),
        ('jakarta_utara', 'Jakarta Utara'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=120)                 
    price_per_hour = models.DecimalField(max_digits=10, decimal_places=2)
    sport_category = models.CharField(max_length=20, choices=SPORT_CHOICES)
    region = models.CharField(max_length=30, choices=JAKARTA_REGION_CHOICES) 

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='equipments'
    )

    quantity = models.PositiveIntegerField(default=1)       
    available = models.BooleanField(default=True)           
    thumbnail = models.URLField()
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['price_per_hour']

    def __str__(self):
        return f"{self.name} ({self.sport_category}) - {self.owner_name}"
