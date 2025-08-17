from django.urls import path
from .import views

app_name = 'classes'

urlpatterns = [
    path('class/main/save/', views.main_classes, name="main_classes")
]