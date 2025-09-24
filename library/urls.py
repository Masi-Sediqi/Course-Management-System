from django.urls import path
from .import views

app_name = 'library'

urlpatterns = [
    path('library/view/', views.library_view, name="library_view"),
    path('library/view/delete/category/<int:id>', views.delete_category, name="delete_category"),
    path('library/view/edit/category/<int:id>', views.edit_category, name="edit_category"),

    path('library/view/delete/station/<int:id>', views.delete_station, name="delete_station"),
    path('library/view/edit/station/<int:id>', views.edit_station, name="edit_station"),

    path('library/view/delete/book/<int:id>', views.delete_book, name="delete_book"),
    path('library/view/edit/book/<int:id>', views.edit_book, name="edit_book"),
    path('library/category/item/s/<int:id>', views.find_category_item, name="find_category_item"),
    path('library/buy/book/again/<int:id>', views.buy_book_again, name="buy_book_again"),
    path('library/buy/book/delete/<int:id>', views.delete_buy_again, name="delete_buy_again"),
    path('library/update/book/price/<int:id>', views.update_per_price, name="update_per_price"),
    path('library/update/stationery/price/<int:id>', views.update_stationery_per_price, name="update_stationery_per_price"),
    path('library/buy/stationery/again/<int:id>', views.buy_stationery_again, name="buy_stationery_again"),

]