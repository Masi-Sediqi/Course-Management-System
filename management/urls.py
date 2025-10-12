from django.urls import path
from .import views

app_name = "management"

urlpatterns = [
    path('Total_income', views.Total_income, name="Total_income"),
    path('delete_income/<int:income_id>/', views.delete_income, name='delete_income'),
    path('edit_income/<int:income_id>/', views.edit_income, name='edit_income'),
    path('delete_expense/<int:expense_id>/', views.delete_expense, name='delete_expense'),
    path('edit_expense/<int:expense_id>/', views.edit_expense, name='edit_expense'),
]