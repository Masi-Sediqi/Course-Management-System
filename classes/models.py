from django.db import models
from library.models import Books
from teachers.models import Teacher
from subjects.models import Subjects
import jdatetime



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
    





    def get_remaining_days(self):
            """محاسبه روزهای باقی مانده بر اساس تاریخ جلالی"""
            try:
                # ✅ تغییر فرمت به DD/MM/YYYY
                end_jalali = jdatetime.datetime.strptime(self.end_date, "%d/%m/%Y").date()
                today_jalali = jdatetime.date.today()
                remaining = (end_jalali - today_jalali).days
                return max(remaining, 0)
            except Exception as e:
                print("DEBUG: Error parsing date:", self.end_date, "| Exception:", e)
                return None

    def is_expired(self):
        remaining = self.get_remaining_days()
        return remaining == 0