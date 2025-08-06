from django.urls import path
from . import views

app_name = "teachers"

urlpatterns = [
    path('teacher/registration/', views.teacher_registration, name="teacher_registration"),
    path('teacher/deactive/<int:id>/', views.deactive_teacher, name="deactive_teacher"),
    path('teacher/active/<int:id>/', views.active_teacher, name="active_teacher"),
    path('teacher/off/', views.off_teachers, name="off_teachers"),
]