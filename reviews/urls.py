from django.urls import path
from reviews.views import (
    show_reviews, 
    get_reviews_json, 
    add_review_ajax, 
    get_review_detail_json,
    edit_review_ajax,  
    delete_review_ajax
)

app_name = 'reviews'

urlpatterns = [
    path('', show_reviews, name='show_reviews'),
    path('get-reviews/', get_reviews_json, name='get_reviews_json'),
    path('add-review/', add_review_ajax, name='add_review_ajax'),
    path('get-review-detail/<int:review_id>/', get_review_detail_json, name='get_review_detail_json'),
    path('edit-review/<int:review_id>/', edit_review_ajax, name='edit_review_ajax'),
    path('delete-review/<int:review_id>/', delete_review_ajax, name='delete_review_ajax'),
]
