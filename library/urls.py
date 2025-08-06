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
]