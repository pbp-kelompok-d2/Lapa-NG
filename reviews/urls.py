from django.urls import path
from reviews.views import show_reviews, get_reviews_json, add_review_ajax

app_name = 'reviews'

urlpatterns = [
    path('', show_reviews, name='show_reviews'),
    path('get-reviews/', get_reviews_json, name='get_reviews_json'),
    path('add-review/', add_review_ajax, name='add_review_ajax'),
]