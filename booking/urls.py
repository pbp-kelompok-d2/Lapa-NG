from django.urls import path
from booking.views import show_booking, create_venue, show_venue, show_xml, show_json, show_json_by_id, show_xml_by_id

app_name = 'booking'

urlpatterns = [
    path('', show_booking, name='show_booking'),
    path('create-venue/', create_venue, name='create_venue'),
    path('venue/<str:id>/', show_venue, name='show_venue'),
    path('xml/', show_xml, name='show_xml'),
    path('json/', show_json, name='show_json'),
    path('xml/<str:news_id>/', show_xml_by_id, name='show_xml_by_id'),
    path('json/<str:news_id>/', show_json_by_id, name='show_json_by_id'),
]