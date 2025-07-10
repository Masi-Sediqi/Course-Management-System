from django.db import models

# Create your models here.

class Student(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    father_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, blank=True, null=True)
    date_of_registration = models.CharField(max_length=20)
    gender = models.CharField(max_length=10, choices=[('Male', 'مرد'), ('Female', 'زن')])
    time = models.CharField(max_length=30)
    subject = models.CharField(max_length=50)
    orginal_fees = models.FloatField()  # <--- This is your فیس
    registered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Student_fess_info(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    orginal_fees = models.FloatField(blank=False)  # <--- This is your فیس
    give_fees = models.FloatField(blank=False)  # <--- This is your فیس
    date = models.CharField(max_length=15, blank=False)
    description = models.TextField(blank=True, null=True)
    