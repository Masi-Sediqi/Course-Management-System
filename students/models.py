from django.db import models

# Create your models here.

class Student(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    date_of_registration = models.CharField(max_length=20)
    gender = models.CharField(max_length=10, choices=[('Male', 'مرد'), ('Female', 'زن')])
    orginal_fees = models.FloatField()  # <--- This is your فیس
    give_fees = models.FloatField()  # <--- This is your فیس
    registered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"