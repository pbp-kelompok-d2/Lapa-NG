from django.db import models
from django.conf import settings
from main.models import Venue
from datetime import datetime, timedelta


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
    borrower_name = models.CharField(
        max_length=100,
        help_text="Nama orang yang akan menggunakan lapangan"
    )
    booking_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    total_price = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Otomatis dihitung dari durasi × harga venue"
    )

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
        return f"{self.user.username} - {self.venue.name} ({self.booking_date})"

    def save(self, *args, **kwargs):
        """
        Hitung otomatis total_price berdasarkan lama booking (jam × harga venue)
        sebelum disimpan ke database.
        """
        if self.start_time and self.end_time and self.venue.price:
            # pastikan end_time > start_time
            start_dt = datetime.combine(self.booking_date, self.start_time)
            end_dt = datetime.combine(self.booking_date, self.end_time)
            duration = (end_dt - start_dt).total_seconds() / 3600  # jam
            if duration > 0:
                self.total_price = int(self.venue.price * duration)
        super().save(*args, **kwargs)
