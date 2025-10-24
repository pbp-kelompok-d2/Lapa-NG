from django.urls import path
from equipment.views import equipment_list, equipment_create, edit_equipment, delete_equipment

app_name = 'equipment'

urlpatterns = [
    path('equipment/', equipment_list, name='equipment_list'),
    path('add-equipment/', equipment_create, name='add_equipment'),
    path('equipment/edit/<uuid:id>/', edit_equipment, name='edit_equipment'),
    path('delete-equipment/<uuid:id>/', delete_equipment, name='delete_equipment'),
]