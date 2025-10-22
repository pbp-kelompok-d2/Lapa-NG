from django.urls import path
from .views import show_feed_main, create_post, show_post, show_xml, show_json, show_xml_by_id, show_json_by_id

app_name = 'feeds'

urlpatterns = [
    path('', show_feed_main, name='show_feed_main'),
    path('create/', create_post, name='create_post'),
    path('post/<str:id>/', show_post, name='show_post'),
    path('xml/', show_xml, name='show_xml'),
    path('json/', show_json, name='show_json'),
    path('xml/<str:post_id>/', show_xml_by_id, name='show_xml_by_id'),
    path('json/<str:post_id>/', show_json_by_id, name='show_json_by_id'),
]
