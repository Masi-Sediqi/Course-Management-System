from django.urls import path
from .import views

app_name = 'library'

urlpatterns = [
    path('library/view/', views.library_view, name="library_view"),
    path('library/view/delete/item/<int:id>', views.delete_item, name="delete_item"),
    path('library/view/edit/item/<int:id>', views.edit_item, name="edit_item"),
    path('library/view/info/item/<int:id>', views.item_info, name="item_info"),
    path('library/purchase/item/<int:id>', views.purchase_item, name="purchase_item"),
    path('library/delete/purchase/item/<int:id>', views.delete_purchase_item, name="delete_purchase_item"),
    path('library/edit/purchase/item/<int:id>', views.edit_purchase_item, name="edit_purchase_item"),]