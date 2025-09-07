from django.urls import path
from . import views

app_name = "teachers"

urlpatterns = [
    path('teacher/registration/', views.teacher_registration, name="teacher_registration"),
    path('teacher/deactive/<int:id>/', views.deactive_teacher, name="deactive_teacher"),
    path('teacher/active/<int:id>/', views.active_teacher, name="active_teacher"),
    path('teacher/off/', views.off_teachers, name="off_teachers"),
    path('teacher/edit/section/<int:id>/', views.edit_teacher, name="edit_teacher"),
    path('teacher/detail/<int:id>/', views.teacher_detail, name="teacher_detail"),
    path('teacher/paid/salary/<int:id>/', views.teacher_paid_salary, name="teacher_paid_salary"),
    path('teacher/loan/request/<int:id>/', views.teacher_loan, name="teacher_loan"),
    path('teacher/paid/remain/money/<int:id>/👎', views.teacher_paid_remain_money, name="teacher_paid_remain_money"),
    path("teachers/<int:teacher_id>/attendance/add/", views.add_attendance, name="add_attendance"),
]