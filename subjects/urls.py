from django.urls import path
from .import views

app_name = "subjects"

urlpatterns = [
    path('main/page/subjects', views.subjects, name="subjects")
]