from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Reviews(models.Model):
    SPORT_CHOICES = [
        ('soccer', 'Soccer'),
        ('tennis', 'Tennis'),
        ('badminton', 'Badminton'),
        ('futsal', 'Futsal'),
        ('basket', 'Basket'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    venue_name = models.CharField(max_length=255)
    sport_type = models.CharField(max_length=20, choices=SPORT_CHOICES, default='soccer')
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField()
    image_url = models.URLField(max_length=2000, null=True, blank=True, help_text="(opsional)")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']  
    
    def __str__(self):
        return f"{self.venue_name} - {self.rating}★ by {self.user.username}"