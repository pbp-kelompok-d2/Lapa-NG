from django.urls import path
from authentication.views import *

app_name = 'authentication'

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('dashboard/', show_dashboard, name='show_dashboard'),
    path("admin-dashboard/", admin_dashboard, name="admin_dashboard"),
    path('api/edit-profile/', edit_profile, name='edit_profile'),
    path('api/delete-profile/', delete_profile, name='delete_profile'),
]