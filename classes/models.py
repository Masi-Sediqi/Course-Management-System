from django.db import models
from library.models import Item
from teachers.models import Teacher


class SubClass(models.Model):
    name = models.CharField(max_length=60)  # مثلاً "ریاضیات - گروه A"
    start_date = models.CharField(max_length=15)  # تاریخ شروع کلاس
    teacher = models.ManyToManyField(Teacher)  # مدرس
    books = models.ManyToManyField(Item)
    fees = models.IntegerField(blank=False)
    capacity = models.PositiveIntegerField(default=30)  # ظرفیت کلاس
    room = models.CharField(max_length=50, blank=True)  # شماره یا نام اتاق
    schedule = models.TextField(blank=True)  # برنامه روزها و ساعت‌های کلاس
    time = models.CharField(max_length=50)
    active = models.BooleanField(default=True)  # فعال/غیرفعال بودن کلاس

    def __str__(self):
        return f"{self.name}"