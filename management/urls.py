from django.urls import path
from .import views

app_name = "management"

urlpatterns = [
    path('Total_income', views.Total_income, name="Total_income")
]