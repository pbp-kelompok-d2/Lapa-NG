from django.db import models
from django.conf import settings
from main.models import Venue

class Booking(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bookings"
    )
    venue = models.ForeignKey(
        Venue,
        on_delete=models.CASCADE,
        related_name="bookings"
    )
    booking_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    total_price = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("confirmed", "Confirmed"),
            ("cancelled", "Cancelled")
        ],
        default="pending"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.venue.name} ({self.booking_date})"
