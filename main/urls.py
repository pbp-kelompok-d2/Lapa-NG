from django.urls import path
from main.views import show_main, import_venues_from_csv

app_name = 'main'

urlpatterns = [
    path('', show_main, name='show_main'),
    path("admin/import-venues/", import_venues_from_csv, name="import_venues_csv"),
]