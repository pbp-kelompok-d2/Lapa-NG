from django.urls import path
from booking.views import booking_page, add_to_cart, checkout_page, view_cart

app_name = 'booking'

urlpatterns = [
    path('', booking_page, name='booking_page'),
    path("add/<int:venue_id>/", add_to_cart, name="add_to_cart"),
    path("checkout/", checkout_page, name="checkout_page"),
    path('cart/', view_cart, name='view_cart'),
]