from django.db import models
from library.models import *
from teachers.models import *
from classes.models import *
import jdatetime
# Create your models here.

class Student(models.Model):
    first_name = models.CharField(max_length=100, blank=False)
    last_name = models.CharField(max_length=100)
    father_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, blank=True, null=True)
    date_of_registration = models.CharField(max_length=20)
    gender = models.CharField(max_length=10, choices=[('Male', 'مرد'), ('Female', 'زن')])
    classs = models.ManyToManyField(SubClass)
    # time = models.CharField(max_length=30)
    # teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, blank=True, null=True)
    # subject = models.CharField(max_length=50)
    # books = models.ManyToManyField(Books)
    # orginal_fees = models.FloatField()  # <--- This is your فیس
    registered_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to="student/", blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


        
class StudentWithoutClass(models.Model):
    first_name = models.CharField(max_length=100 , blank=False)
    last_name = models.CharField(max_length=100 , blank=True)
    father_name = models.CharField(max_length=100 , blank=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    date = models.CharField(max_length=20, blank=False)
    gender = models.CharField(max_length=10, choices=[('Male', 'مرد'), ('Female', 'زن')])
    date_for_notification = models.CharField(max_length=14, blank=False)
    jalali_to_gregorian = models.DateField()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def is_notification_today(self):
        """Check if today is notification day."""
        today = jdatetime.date.today().togregorian()
        return self.jalali_to_gregorian == today
        

class Student_fess_info(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    st_class = models.ForeignKey(SubClass, on_delete=models.SET_NULL, blank=True, null=True)
    orginal_fees = models.FloatField(blank=False)
    give_fees = models.FloatField(blank=False)
    remain_fees = models.FloatField(blank=True, null=True)
    date = models.CharField(max_length=15, blank=False)
    description = models.TextField(blank=True, null=True)
    month = models.CharField(max_length=120)
    remaining = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

class StudentGiveRemainMoney(models.Model):
    studnet = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True)
    date = models.CharField(max_length=15, blank=False)
    amount = models.FloatField(blank=False)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class StudentRemailMoney(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="student_remains", blank=True, null=True)
    amount = models.FloatField()

class BuyBook(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True)
    date = models.CharField(max_length=14, blank=False)
    book = models.ManyToManyField(Books, blank=False)
    number_of_book = models.IntegerField(default=1)
    total_amount = models.FloatField()
    paid_amount = models.FloatField(blank=False)
    remain_amount = models.FloatField(default=0)
    description = models.TextField(blank=True)

class BookRecord(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True)
    book = models.ForeignKey(Books, on_delete=models.CASCADE)
    buy_book = models.ForeignKey(BuyBook, on_delete=models.CASCADE)
    date = models.CharField(max_length=14, blank=False)
    number_of_book = models.IntegerField(default=1)
    total_amount = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

class BuyStationery(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True) 
    date = models.CharField(max_length=14, blank=False)
    stationery = models.ManyToManyField(StationeryItem)
    number_of_stationery = models.IntegerField(default=1)
    total_stationery_amount = models.FloatField()
    paid_stationery_amount = models.FloatField(blank=False)
    remain_amount = models.FloatField(default=0)
    description = models.TextField(blank=True)

class StationeryRecord(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True)
    stationery = models.ForeignKey(StationeryItem, on_delete=models.CASCADE)
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