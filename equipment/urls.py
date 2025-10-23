from django.urls import path
from equipment.views import equipment_list

app_name = 'equipment'

urlpatterns = [
    path('equipment/', equipment_list, name='equipment_list'),
]