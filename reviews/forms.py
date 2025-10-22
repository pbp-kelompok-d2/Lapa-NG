from django.forms import ModelForm
from reviews.models import Reviews

class ReviewForm(ModelForm):
    class Meta:
        model = Reviews
        fields = ["venue_name", "rating", "comment"]