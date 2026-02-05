from django.db import models

# Create your models here.

class TotalBalance(models.Model):
    total_income = models.FloatField(default=0)
    total_expenses = models.FloatField(default=0)
    
    # money others owe us
    total_receivable = models.FloatField(default=0)

    # money we owe others
    total_payable = models.FloatField(default=0)

    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.total_income < 0:
            self.total_income = 0
        if self.total_expenses < 0:
            self.total_expenses = 0
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Income: {self.total_income} | Expenses: {self.total_expenses}"

class FinanceRecord(models.Model):
    TYPE_CHOICES = (
        ('income', 'عاید'),
        ('expense', 'مصرف'),
    )

    date = models.CharField(max_length=14)
    amount = models.FloatField()
    description = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)

    def __str__(self):
        return f"{self.type.upper()} - {self.amount}"