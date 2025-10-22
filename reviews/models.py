from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Reviews(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    venue_name = models.CharField(max_length=255)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']  
    
    def __str__(self):
        return f"{self.venue_name} - {self.rating}★ by {self.user.username}"