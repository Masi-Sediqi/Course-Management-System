from django.urls import path
from . import views

app_name = 'settings'

urlpatterns = [
    path('setting-main/', views.settings, name='settings'), # Example URL pattern
    path('delete-database/', views.delete_database, name='delete_database'), # Example URL pattern
]