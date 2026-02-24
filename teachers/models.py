from django.db import models
from students.models import *
from django.db.models.signals import post_save
from django.dispatch import receiver
import jdatetime

class Teacher(models.Model):
    GENDER_CHOICES = [
        ('M', 'مرد'),
        ('F', 'زن'),
    ]
    name = models.CharField(max_length=100, blank=False)
    phone = models.CharField(max_length=10, blank=True)
    gender = models.CharField(max_length=120, choices=GENDER_CHOICES)
    image = models.ImageField(upload_to="teacher/", blank=True)
    percentage = models.FloatField(blank=True, default=0)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    deactivate_at = models.CharField(max_length=15, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.name}'

@receiver(post_save, sender=Teacher)
def create_req_approve(sender, instance, created, **kwargs):
    if created:
        TeacherBalance.objects.create(teacher=instance, total_paid=0, total_remain=0, total_loan=0)
    

class TeacherPaidSalary(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True)
    date = models.CharField(max_length=14, blank=False)
    amount = models.FloatField()
    paid_salary = models.FloatField()
    remain_salary = models.FloatField(default=0)
    description = models.TextField(blank=True)
    loan_amount = models.FloatField(default=0)


class TeacherLoan(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    date = models.CharField(max_length=12, blank=False)
    amount = models.IntegerField(blank=False)
    description = models.TextField(blank=True)


class AttendanceAndLeaves(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    start_date = models.CharField(max_length=10)  # e.g., "28/02/1404"
    number_of_day = models.FloatField()
    end_date = models.CharField(max_length=10, blank=True)  # auto-calculated
    description = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        try:
            day, month, year = map(int, self.start_date.split('/'))
            start_j = jdatetime.date(year, month, day)
            # subtract 1 because start_date counts as the first day
            end_j = start_j + jdatetime.timedelta(days=int(self.number_of_day) - 1)
            self.end_date = f"{end_j.day:02d}/{end_j.month:02d}/{end_j.year}"
        except Exception:
            self.end_date = self.start_date  # fallback if invalid date
        super().save(*args, **kwargs)

    @property
    def days(self):
        return self.number_of_day
    

class TeacherBalance(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    total_paid = models.FloatField(default=0)
    total_remain = models.FloatField(default=0)
    total_loan = models.FloatField(default=0)

    def save(self, *args, **kwargs):
        # Prevent negative values
        self.total_paid = max(0, self.total_paid)
        self.total_remain = max(0, self.total_remain)
        self.total_loan = max(0, self.total_loan)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.teacher.name}'