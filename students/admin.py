from django.contrib import admin

from students.models import Student, Student_fess_info

# Register your models here.

admin.site.register(Student)
admin.site.register(Student_fess_info)