from django.urls import path
from booking.views import booking_page, add_to_cart, checkout_page, edit_booking, remove_from_cart, checkout_confirm, view_cart, booking_list, clear_booking
from booking.views import api_create_booking, api_list_bookings, api_delete_booking, api_update_booking, api_update_booking_status

app_name = 'booking'

urlpatterns = [
    path('', booking_page, name='booking_page'),
    path("add/<int:venue_id>/", add_to_cart, name="add_to_cart"),
    path("checkout/", checkout_page, name="checkout_page"),
    path('edit/<int:venue_id>/', edit_booking, name='edit_booking'),
    path('remove/<int:venue_id>/', remove_from_cart, name='remove_from_cart'),
    path('checkout/confirm/', checkout_confirm, name='checkout_confirm'),
    path('cart/', view_cart, name='view_cart'),
    path('booking-list/', booking_list, name='booking_list'),
    path('clear/<int:booking_id>/', clear_booking, name='clear_booking'),
    path("api/create/", api_create_booking, name="api_create_booking"),
    path("api/list/<int:user_id>/", api_list_bookings, name="api_list_bookings"),
    path("api/delete/<int:booking_id>/", api_delete_booking, name="api_delete_booking"),
    path("api/update/<int:booking_id>/", api_update_booking, name="api_update_booking"),
    path("api/update-status/<int:booking_id>/", api_update_booking_status, name="api_update_"),
]