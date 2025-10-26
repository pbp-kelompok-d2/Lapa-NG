from django.db import models
from django.utils.text import slugify
from django.conf import settings
from django.templatetags.static import static

class Venue(models.Model):
    CATEGORIES = [
        ('soccer', 'Soccer'),
        ('tennis', 'Tennis'),
        ('badminton', 'Badminton'),
        ('futsal', 'Futsal'),
        ('basketball', 'Basketball'),
        ('multi-sport', 'Multi-Sport'),
        ('other', 'Other'), 
    ]
    # -----------------------------

    id = models.AutoField(primary_key=True) 
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="venues",
        null=True, 
        blank=True 
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)

    category = models.CharField(
        max_length=20,
        choices=CATEGORIES,  
        default='other'
    )
    
    description = models.TextField(blank=True, help_text="A short description of the venue.")

    address = models.TextField(blank=True)

    price = models.PositiveIntegerField(
        null=True, 
        blank=True,
        help_text="Price in Rupiah per hour (e.g., 50000)"
    )
    capacity = models.PositiveIntegerField(
        null=True, 
        blank=True,
        help_text="Maximum number of people"
    )

    opening_time = models.TimeField(null=True, blank=True)
    closing_time = models.TimeField(null=True, blank=True)

    time_display = models.CharField(
        max_length=50, 
        blank=True,
        editable=False 
    )
    thumbnail = models.CharField(
        max_length=200, 
        blank=True,
        help_text="e.g., my_venue.jpg or a URL https://..."
    )

    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


    #ngecek thumbnail apakah local file atau url
    @property
    def thumbnail_url(self):
        if self.thumbnail:
            # Check if it's already a full URL
            if self.thumbnail.startswith('http://') or self.thumbnail.startswith('https://'):
                return self.thumbnail
            else:
                # It's a local filename (e.g., "soccer.jpg"), build a static path
                return static(f'images/{self.thumbnail}')
        
        # No thumbnail provided, return a default placeholder
        return static('images/No_Image_Available.jpg')

    class Meta:
        ordering = ["name"]
        indexes = [models.Index(fields=["category"]), models.Index(fields=["price"])]
        unique_together = [("name", "address")]

    def save(self, *args, **kwargs):
        # Auto-generate slug
        if not self.slug and self.name:
            base = slugify(self.name) or "venue"
            slug = base
            i = 1
            while Venue.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                i += 1
                slug = f"{base}-{i}"
            self.slug = slug
        
        # auto -generate time_display
        if self.opening_time and self.closing_time:
            self.time_display = f"{self.opening_time.strftime('%H:%M')} - {self.closing_time.strftime('%H:%M')}"
        else:
            self.time_display = "N/A"
            
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
