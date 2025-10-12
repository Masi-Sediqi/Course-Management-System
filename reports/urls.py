from django.urls import path
from . import views

app_name = "reports"

urlpatterns = [
    path("reports/all/standard", views.statndart, name="standard"),
    path("reports/students/reports/", views.students_reports, name="students_reports"),
    path("reports/teachers/reports/", views.teachers_reports, name="teachers_reports"),
    path("reports/books/reports/", views.books_reports, name="books_reports"),
    path("reports/income/expenses/reports/", views.income_expenses, name="income_expenses"),
]