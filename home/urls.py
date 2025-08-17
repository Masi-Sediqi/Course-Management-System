from django.urls import path
from . import views

app_name = "home"

urlpatterns = [
    path('', views.dashboard, name="dashboard"),
    path('colculator', views.colculator, name="colculator")
]