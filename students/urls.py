from django.urls import path
from . import views

app_name ='students'

urlpatterns = [
    path('student/registration', views.students_registration, name="students_registration"),
    path('student/registration/<int:id>/delete', views.delete_students, name="delete_students"),
    path('student/registration/<int:id>/edit', views.edit_students, name="edit_students"),
    path('student/registration-bill/<int:id>', views.student_bill, name="student_bill"),
    path('student/<int:student_id>/', views.student_detail, name='student_detail'),
    path('student/fees_info/<int:student_id>/', views.student_fees_detail, name='student_fees_detail'),
]
