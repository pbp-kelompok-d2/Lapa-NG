from django.urls import path
from booking.views import booking_by_venue, venue_list, show_venue

app_name = 'booking'

urlpatterns = [
    path("", venue_list, name="venue_list"),
    path("venue/<int:venue_id>/book/", booking_by_venue, name="booking_by_venue"),
    path('<int:venue_id>/detail/', show_venue, name='show_venue'),
]