from django.urls import path
from . import views

app_name = "home"

urlpatterns = [
    path('', views.dashboard, name="dashboard"),
    path('history', views.history, name="history"),
    path('supplier', views.supplier, name="supplier"),
    path('delete_supplier/<int:id>/', views.delete_supplier, name="delete_supplier"),
    path('edit_supplier/<int:id>/', views.edit_supplier, name="edit_supplier"),
    path('supplier_detail/<int:id>/', views.supplier_detail, name="supplier_detail"),
    path('delete_balance/<int:id>/', views.delete_balance, name="delete_balance"),
    path('edit_balance/<int:id>/', views.edit_balance, name="edit_balance"),
    path('notifications/mark-read/<int:notification_id>/', views.mark_as_read, name='mark_as_read'),
    path('notifications/mark-unread/<int:notification_id>/', views.mark_as_unread, name='mark_as_unread'),
    path('notifications/mark-all-read/', views.mark_all_as_read, name='mark_all_as_read'),
    path('about_us/', views.about_us, name='about_us'),
    path('hearning/', views.hearning, name='hearning'),
]