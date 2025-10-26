from django.db import models
import uuid
from django.contrib.auth.models import User

class Post(models.Model):
    CATEGORY_CHOICES = [
        ('soccer', 'Soccer'),
        ('futsal', 'Futsal'),
        ('basket', 'Basket'),
        ('badminton', 'Badminton'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='soccer')
    thumbnail = models.URLField(blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    post_views = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        uname = self.user.username if self.user else "Anonymous"
        return f"{uname} - {self.get_category_display()}"

    def increment_views(self):
        self.post_views += 1
        self.save(update_fields=['post_views'])
    
    @property
    def is_post_hot(self):
        return self.post_views > 10