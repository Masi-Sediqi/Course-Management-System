from django.urls import path
from . import views

app_name = "home"

urlpatterns = [
    path('', views.dashboard, name="dashboard"),
    path('colculator', views.colculator, name="colculator"),
    path('supplier', views.supplier, name="supplier"),
    path('delete_supplier/<int:id>/', views.delete_supplier, name="delete_supplier"),
    path('edit_supplier/<int:id>/', views.edit_supplier, name="edit_supplier"),
]