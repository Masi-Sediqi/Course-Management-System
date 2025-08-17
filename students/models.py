from django.db import models
from library.models import *
from teachers.models import *
from classes.models import *
# Create your models here.

class Student(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    father_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, blank=True, null=True)
    date_of_registration = models.CharField(max_length=20)
    gender = models.CharField(max_length=10, choices=[('Male', 'مرد'), ('Female', 'زن')])
    classs = models.ManyToManyField(SubClass)
    # time = models.CharField(max_length=30)
    # teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, blank=True, null=True)
    # subject = models.CharField(max_length=50)
    # books = models.ManyToManyField(Books)
    # orginal_fees = models.FloatField()  # <--- This is your فیس
    registered_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to="student/")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Student_fess_info(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    orginal_fees = models.FloatField(blank=False)  # <--- This is your فیس
    give_fees = models.FloatField(blank=False)  # <--- This is your فیس
    remain_fees = models.FloatField(blank=True, null=True)
    date = models.CharField(max_length=15, blank=False)
    description = models.TextField(blank=True, null=True)
    month = models.CharField(max_length=120)
    remaining = models.FloatField(default=0)

class StudentRemailMoney(models.Model):
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, related_name="student_remains", blank=True, null=True)
    amount = models.FloatField()

class StudentGiveRemainMoney(models.Model):
    studnet = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.CharField(max_length=15, blank=False)
    amount = models.FloatField(blank=False)
    description = models.TextField()

class StudentImporvment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True)
    date = models.CharField(max_length=14, blank=False)
    past_book = models.ForeignKey(Books, on_delete=models.SET_NULL, null=True, related_name="books")
    change_book = models.ForeignKey(Books, on_delete=models.SET_NULL, null=True)
    file = models.FileField(upload_to=f"student/", blank=True)
    description = models.TextField(blank=True)

class BuyBook(models.Model):
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True)
    date = models.CharField(max_length=14, blank=False)
    book = models.ManyToManyField(Books, blank=False)
    paid_amount = models.FloatField(blank=False)
    remain_amount = models.FloatField(default=0)
    description = models.TextField(blank=True)