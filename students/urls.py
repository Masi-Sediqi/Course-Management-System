from django.urls import path
from . import views

app_name ='students'

urlpatterns = [
    path('student/registration', views.students_registration, name="students_registration"),
    path('student/registration/<int:id>/delete', views.delete_students, name="delete_students"),
    path('student/without-class/<int:id>/delete', views.delete_students_withoutclass, name="delete_students_withoutclass"),
    path('student/registration/<int:id>/edit', views.edit_students, name="edit_students"),
    path("students_edit/<int:id>/", views.students_edit_withoutclass, name="students_edit_withoutclass"),  # 🔹 new url
    path('student/registration-bill/<int:student_id>/<int:fees_id>/', views.student_bill, name="student_bill"),
    path('student/<int:student_id>/', views.student_detail, name='student_detail'),
    path('student/fees_info/<int:student_id>/', views.student_fees_detail, name='student_fees_detail'),
    path('student/activation/<int:student_id>/', views.student_activate, name='student_activate'),
    path('student/activation-on/<int:student_id>/', views.student_activate_on, name='student_activate_on'),
    path('student/activation/off!/', views.off_students, name='off_students'),
    path('student/with-out-class/nothing!/', views.students_without_class, name='students_without_class'),
    path('student/improvment/top/<int:id>/', views.student_improvment, name='student_improvment'),
    path('student/buy/book/<int:id>/', views.buy_book, name='buy_book'),
]
