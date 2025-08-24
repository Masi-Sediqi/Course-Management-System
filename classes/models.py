from django.db import models
from library.models import Books
from teachers.models import Teacher
from subjects.models import Subjects

# Create your models here.
class MainClass(models.Model):
    name = models.CharField(max_length=60)  # نام کورس، مثلاً "ریاضیات"
    description = models.TextField(blank=True)  # توضیحات کلی کورس
    created = models.DateField(auto_now_add=True)
    active = models.BooleanField(default=True)  # آیا این دوره فعال است؟

    def __str__(self):
        return self.name


class SubClass(models.Model):
    main_class = models.ForeignKey(MainClass, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=60)  # مثلاً "ریاضیات - گروه A"
    start_date = models.CharField(max_length=15)  # تاریخ شروع کلاس
    end_date = models.CharField(max_length=15)
    teacher = models.ManyToManyField(Teacher)  # مدرس
    books = models.ManyToManyField(Books)
    # subjects = models.ManyToManyField(Subjects)
    fees = models.IntegerField(blank=False)
    capacity = models.PositiveIntegerField(default=30)  # ظرفیت کلاس
    room = models.CharField(max_length=50, blank=True)  # شماره یا نام اتاق
    schedule = models.TextField(blank=True)  # برنامه روزها و ساعت‌های کلاس
    time = models.CharField(max_length=50)
    active = models.BooleanField(default=True)  # فعال/غیرفعال بودن کلاس

    def __str__(self):
        return f"{self.name}"