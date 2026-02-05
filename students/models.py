from django.db import models
from library.models import *
from teachers.models import *
from classes.models import *
import jdatetime
# Create your models here.

class Student(models.Model):
    first_name = models.CharField(max_length=100, blank=False)
    father_name = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=[('Male', 'مرد'), ('Female', 'زن')])
    registered_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to="student/", blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.first_name}"

class Student_fess_info(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    st_class = models.ForeignKey(SubClass, on_delete=models.SET_NULL, blank=True, null=True)
    orginal_fees = models.FloatField(blank=False)
    give_fees = models.FloatField(blank=False)
    remain_fees = models.FloatField(blank=True, null=True)
    date = models.CharField(max_length=15, blank=False)
    end_date = models.CharField(max_length=15, blank=True)
    description = models.TextField(blank=True, null=True)
    month = models.CharField(max_length=120)
    not_remain = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class BuyBook(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True)
    date = models.CharField(max_length=14, blank=False)
    book = models.ManyToManyField(Item, blank=False)
    number_of_book = models.IntegerField(default=1)
    total_amount = models.FloatField()
    paid_amount = models.FloatField(blank=False)
    remain_amount = models.FloatField(default=0)
    description = models.TextField(blank=True)

class BookRecord(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True)
    book = models.ForeignKey(Item, on_delete=models.CASCADE)
    buy_book = models.ForeignKey(BuyBook, on_delete=models.CASCADE)
    date = models.CharField(max_length=14, blank=False)
    number_of_book = models.IntegerField(default=1)
    total_amount = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

class BuyStationery(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True) 
    date = models.CharField(max_length=14, blank=False)
    stationery = models.ManyToManyField(Item)
    number_of_stationery = models.IntegerField(default=1)
    total_stationery_amount = models.FloatField()
    paid_stationery_amount = models.FloatField(blank=False)
    remain_amount = models.FloatField(default=0)
    description = models.TextField(blank=True)

class StationeryRecord(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True)
    stationery = models.ForeignKey(Item, on_delete=models.CASCADE)
    buy_stationery = models.ForeignKey(BuyStationery, on_delete=models.CASCADE)
    date = models.CharField(max_length=14, blank=False)
    number_of_stationery = models.IntegerField(default=1)
    total_amount = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

class StudentImporvment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True)
    date = models.CharField(max_length=14, blank=False)
    past_class = models.ForeignKey(SubClass, on_delete=models.CASCADE, null=True, related_name="past_class")
    number = models.FloatField(blank=False)
    after_class = models.ForeignKey(SubClass, on_delete=models.CASCADE, null=True, related_name="after_class")
    file = models.FileField(upload_to=f"student/", blank=True)
    description = models.TextField(blank=True)



class StudentBalance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True)
    date = models.CharField(max_length=14, blank=False)
    paid = models.FloatField(default=0)
    remain = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)