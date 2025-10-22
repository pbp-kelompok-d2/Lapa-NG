from django.urls import path
from main.views import (
    show_main, venue_detail, create_venue, edit_venue, delete_venue,
    import_venues_from_csv, 
) 

app_name = 'main'

urlpatterns = [
    path('', show_main, name='show_main'),
    path('venue/add/', create_venue, name='create_venue'), 
    path('venue/<slug:slug>/', venue_detail, name='venue_detail'), 
    path('venue/<slug:slug>/edit/', edit_venue, name='edit_venue'),  
    path('venue/<slug:slug>/delete/', delete_venue, name='delete_venue'),
    path("import-venues-from-csv/", import_venues_from_csv, name="import_venues_csv"),
]