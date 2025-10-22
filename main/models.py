from django.db import models
from django.utils.text import slugify
from django.conf import settings

class Venue(models.Model):
    id = models.AutoField(primary_key=True) 
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="venues",
        null=True, # Allow existing venues (from CSV) to have no owner
        blank=True 
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)

    category = models.CharField(max_length=20)       # langsung pakai string dari CSV
    address = models.TextField(blank=True)

    price = models.PositiveIntegerField(null=True, blank=True)     # rupiah/jam
    capacity = models.PositiveIntegerField(null=True, blank=True)

    opening_time = models.TimeField(null=True, blank=True)
    closing_time = models.TimeField(null=True, blank=True)

    # kolom 'time' di CSV itu teks rentang jam; simpan apa adanya supaya bisa ditampilkan cepat
    time_display = models.CharField(max_length=50, blank=True)
    thumbnail = models.CharField(max_length=200, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        indexes = [models.Index(fields=["category"]), models.Index(fields=["price"])]
        unique_together = [("name", "address")]  # mencegah duplikat sederhana

    def save(self, *args, **kwargs):
        if not self.slug and self.name:
            base = slugify(self.name) or "venue"
            slug = base
            i = 1
            while Venue.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                i += 1
                slug = f"{base}-{i}"
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

