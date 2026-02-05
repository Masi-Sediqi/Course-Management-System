from django.urls import path
from .import views

app_name = "management"

urlpatterns = [
    path('Total_income', views.Total_income, name="Total_income"),
    path('delete_record/<int:record_id>/', views.delete_record, name='delete_record'),
    path('edit_record/<int:record_id>/', views.edit_record, name='edit_record'),
]