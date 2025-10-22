from django.urls import path
from .import views

app_name = 'classes'

urlpatterns = [
    path('class/main/save/', views.main_classes, name="main_classes"),
    path('classes/sub/<int:pk>/edit/', views.edit_sub_class, name='edit_sub_class'),
    path('classes/sub/<int:pk>/delete/', views.delete_sub_class, name='delete_sub_class'),
    path('classes/sub/<int:pk>/deactive/', views.deactive_sub_class, name='deactive_sub_class'),
    path('classes/sub/<int:pk>/active/', views.active_sub_class, name='active_sub_class'),

    path('classes/main/<int:id>/edit/', views.edit_main_class, name='edit_main_class'),
    path('classes/main/<int:id>/delete/', views.delete_main_class, name='delete_main_class'),
]