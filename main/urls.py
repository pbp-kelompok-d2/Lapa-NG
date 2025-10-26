from django.urls import path
from main.views import (
    show_main, venue_detail, filter_venues,
    get_venue_details, get_create_form_html, create_venue_ajax,
    import_venues_from_csv, add_to_booking_draft_stub, get_edit_form_html, edit_venue_ajax, delete_venue_ajax, get_delete_form_html
) 

app_name = 'main'

urlpatterns = [
    path('', show_main, name='show_main'),
    path('venue/<slug:slug>/', venue_detail, name='venue_detail'), 

    # ajax stuff
    path('ajax/filter-venues/', filter_venues, name='filter_venues'),
    path('ajax/venue-details/<slug:slug>/', get_venue_details, name='get_venue_details'),
    path('ajax/get-create-form/', get_create_form_html, name='get_create_form'),
    path('ajax/create-venue/', create_venue_ajax, name='create_venue_ajax'),
    path('ajax/get-edit-form/<slug:slug>/', get_edit_form_html, name='get_edit_form'),
    path('ajax/edit-venue/<slug:slug>/', edit_venue_ajax, name='edit_venue_ajax'),
    path('ajax/delete-venue/<slug:slug>/', delete_venue_ajax, name='delete_venue_ajax'),
    path('ajax/get-delete-form/<slug:slug>/', get_delete_form_html, name='get_delete_form'),

    # misc
    path("import-venues-from-csv/", import_venues_from_csv, name="import_venues_csv"),
    path('ajax/stub-add-to-booking/<int:venue_id>/', add_to_booking_draft_stub, name='stub_add_to_booking'),

]