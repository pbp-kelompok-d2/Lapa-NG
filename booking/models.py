import uuid
from django.db import models

class Venue(models.Model):
    CATEGORY_CHOICES = [
        ('soccer', 'Soccer'),
        ('tennis', 'Tennis'),
        ('futsal', 'Futsal'),
        ('badminton', 'Badminton'),
        ('basketball', 'Basketball'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    price = models.IntegerField()
    capacity = models.IntegerField()
    description = models.TextField()
    time = models.TextField(max_length=255, blank=True, null=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='update')
    thumbnail = models.URLField(blank=True, null=True)
    venue_views = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    is_featured = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name
    
    @property
    def is_venue_hot(self):
        return self.venue_views > 20
        
    def increment_views(self):
        self.venue_views += 1
        self.save()