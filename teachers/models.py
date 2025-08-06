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
    birth_date = models.CharField(max_length=14, blank=True)
    phone = models.CharField(max_length=10, blank=True)
    gender = models.CharField(max_length=120, choices=GENDER_CHOICES)
    subject = models.CharField(max_length=100, blank=False)
    percentage = models.FloatField(blank=False)
    file = models.FileField(upload_to="teacher/", blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.name} {self.last_name}'