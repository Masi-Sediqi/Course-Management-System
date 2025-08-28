from django.db import models
from datetime import datetime
from students.models import *

class Teacher(models.Model):
    GENDER_CHOICES = [
        ('M', 'مرد'),
        ('F', 'زن'),
    ]
    name = models.CharField(max_length=100, blank=False)
    last_name = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=10, blank=True)
    gender = models.CharField(max_length=120, choices=GENDER_CHOICES)
    percentage = models.FloatField(blank=False)
    file = models.FileField(upload_to="teacher/", blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.name} {self.last_name}'

class TeacherPaidSalary(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True)
    date = models.CharField(max_length=14, blank=False)
    amount_of_fees_bell = models.IntegerField()
    amount = models.FloatField()
    paid_salary = models.FloatField()
    remain_salary = models.FloatField(default=0)
    description = models.TextField(blank=True)

class TeacherRemainMoney(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    total_amount = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

class TeacherLoan(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    date = models.CharField(max_length=12, blank=False)
    amount = models.IntegerField(blank=False)
    description = models.TextField(blank=True)

class TeacherTotalLoan(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    total_loan_amount = models.FloatField()