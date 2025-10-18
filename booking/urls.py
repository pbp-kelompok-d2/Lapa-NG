from django.urls import path
from . import views

app_name = 'booking'

urlpatterns = [
    path('', views.home, name='home'),                 # GET /booking/
    path('api/list/', views.api_list, name='api_list'),               # GET daftar booking user (JSON)
    path('api/create/', views.api_create, name='api_create'),         # POST create booking (JSON/form)
    path('api/from-main/', views.api_create_from_main, name='api_from_main'),  # POST dari main (venue_id)
    path('api/search/', views.api_search, name='api_search'),         # GET filter/search venue (stub)
]
