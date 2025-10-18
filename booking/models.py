from django.db import models
from django.contrib.auth.models import User

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')

    # Soft link ke Venue (sementara)
    venue_ref = models.IntegerField(null=True, blank=True, db_index=True)  # calon PK venue jika nanti int
    venue_name = models.CharField(max_length=120, null=True, blank=True)                          # wajib, biar tetap readable
    venue_city = models.CharField(max_length=120, blank=True)              # optional
    sport_type = models.CharField(max_length=50, blank=True)               # optional

    date = models.DateField(null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def to_dict(self):
        return {
            "id": self.id,
            "venue_ref": self.venue_ref,
            "venue_name": self.venue_name,
            "venue_city": self.venue_city,
            "sport_type": self.sport_type,
            "date": self.date.isoformat(),
            "start_time": self.start_time.strftime('%H:%M'),
            "end_time": self.end_time.strftime('%H:%M'),
            "notes": self.notes,
        }
