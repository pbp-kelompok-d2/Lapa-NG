from django.urls import path
from equipment.views import equipment_list, equipment_create, \
    edit_equipment, delete_equipment, show_xml, show_json, \
        show_xml_by_id, show_json_by_id, get_equipment, create_equipment_flutter

app_name = 'equipment'

urlpatterns = [
    path('', equipment_list, name='equipment_list'),
    path('add-equipment/', equipment_create, name='add_equipment'),
    path('edit/<uuid:id>/', edit_equipment, name='edit_equipment'),
    path('delete/<uuid:id>/', delete_equipment, name='delete_equipment'),
    path('xml/', show_xml, name='show_xml'),
    path('json/', show_json, name='show_json'),
    path('xml/<str:id>/', show_xml_by_id, name='show_xml_by_id'),
    path('json/<str:id>/', show_json_by_id, name='show_json_by_id'),
    path('get-equipment/', get_equipment, name='get_equipment'),
    path('create-flutter/', create_equipment_flutter, name='create_equipment_flutter'),
]