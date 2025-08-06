from django.db import models

# Create your models here.

class TotalIncome(models.Model):
    total_amount = models.FloatField(default=0)
    # Optional: last updated time
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Total Income: {self.total_amount} (Updated at {self.updated_at.strftime('%Y-%m-%d %H:%M')})"

class TotalExpenses(models.Model):
    total_amount = models.FloatField(default=0)
    # Optional: last updated time
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Total Income: {self.total_amount} (Updated at {self.updated_at.strftime('%Y-%m-%d %H:%M')})"


class OtherIncome(models.Model):
    date = models.CharField(max_length=14, blank=False)
    amount = models.FloatField()
    description = models.TextField()

class Expenses(models.Model):
    date = models.CharField(max_length=14, blank=False)
    amount = models.FloatField()
    description = models.TextField()