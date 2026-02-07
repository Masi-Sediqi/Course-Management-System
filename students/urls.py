from django.urls import path
from . import views

app_name ='students'

urlpatterns = [
    path('student/registration', views.students_registration, name="students_registration"),
    path('student/registration/<int:id>/delete', views.delete_students, name="delete_students"),
    path('student/registration/<int:id>/edit', views.edit_students, name="edit_students"),
    path('student/registration-bill/<int:student_id>/<int:fees_id>/', views.student_bill, name="student_bill"),
    path('student/<int:student_id>/', views.student_detail, name='student_detail'),
    path('student/fees_info/<int:student_id>/', views.student_fees_detail, name='student_fees_detail'),
    path('student/activation/<int:student_id>/', views.student_activate, name='student_activate'),
    path('student/activation-on/<int:student_id>/', views.student_activate_on, name='student_activate_on'),
    path('student/improvment/top/<int:id>/', views.student_improvment, name='student_improvment'),
    path('student/improvment/delete/<int:id>/', views.delete_student_improvment, name='delete_student_improvment'),
    path('student/improvment/edit/<int:id>/', views.edit_student_improvement, name='edit_student_improvement'),
    path('student/buy/book/<int:id>/', views.buy_book, name='buy_book'),
    path('student/paid/fess/<int:stu_id>/<int:cla_id>/', views.student_paid_fees, name='student_paid_fees'),
    path('student/paid/deleting/<int:id>', views.delete_paid_fess, name='delete_paid_fess'),
    path('student/edit/paid/<int:id>', views.edit_paid_fees, name='edit_paid_fees'),
    path('student/purchased/items/<int:student_id>/<int:item_id>/', views.student_purchased_items, name='student_purchased_items'),
    path('student/purchased/<int:student_id>/', views.student_purchased, name='student_purchased'),
    path('student/payments/<int:student_id>/', views.student_payments, name='student_payments'),
    path('student/delete/purchased/<int:purchase_id>/', views.delete_student_purchased_items, name='delete_student_purchased_items'),
    path('student/edit/purchased/<int:purchase_id>/', views.edit_student_purchased_items, name='edit_student_purchased_items'),
]
