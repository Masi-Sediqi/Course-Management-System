from django.urls import path
from .import views

app_name = 'library'

urlpatterns = [
    path('library/view/', views.library_view, name="library_view"),
    path('library/view/delete/item/<int:id>', views.delete_item, name="delete_item"),
    path('library/view/edit/item/<int:id>', views.edit_item, name="edit_item"),
    path('library/view/info/item/<int:id>', views.item_info, name="item_info"),
    path('library/buy/book/again/<int:id>', views.buy_book_again, name="buy_book_again"),
    path('library/buy/book/delete/<int:id>', views.delete_buy_again, name="delete_buy_again"),
    path('library/update/book/price/<int:id>', views.update_per_price, name="update_per_price"),
]