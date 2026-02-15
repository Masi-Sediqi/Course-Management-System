from django.urls import path
from . import views

app_name = 'settings'

urlpatterns = [
    path('setting-main/', views.settings_page, name='settings'),
    path('backup/', views.generate_backup, name='generate_backup'),
    path('backup/delete/<int:backup_id>/', views.delete_backup, name='delete_backup'),
    ]