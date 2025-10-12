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
    path('teacher/delete/paid/salary/<int:salary_id>/', views.delete_teacher_salary_record, name="delete_teacher_salary_record"),
    path('teacher/edit/paid/salary/<int:salary_id>/', views.edit_teacher_salary_record, name="edit_teacher_salary_record"),
    path('teacher/loan/request/<int:id>/', views.teacher_loan, name="teacher_loan"),
    path('teacher/delete/loan/request/<int:loan_id>/', views.delete_loan_request, name="delete_loan_request"),
    path('teacher/edit/loan/request/<int:loan_id>/', views.edit_loan_request, name="edit_loan_request"),
    path('teacher/paid/remain/money/<int:id>/👎', views.teacher_paid_remain_money, name="teacher_paid_remain_money"),
    path('teacher/delete/paid/remain/money/<int:paid_id>/👎', views.delete_paid_remain_money, name="delete_paid_remain_money"),
    path('teacher/edit/paid/remain/money/<int:paid_id>/', views.edit_paid_remain_money, name="edit_paid_remain_money"),
    path("teachers/<int:teacher_id>/attendance/add/", views.add_attendance, name="add_attendance"),
    path("teachers/<int:attendance_id>/delete/attendance/", views.delete_attendance, name="delete_attendance"),
    path("teachers/<int:attendance_id>/edit/attendance/", views.edit_attendance, name="edit_attendance"),
]