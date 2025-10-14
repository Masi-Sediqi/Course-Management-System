from django.db import models

# Create your models here.

class TotalIncome(models.Model):
    total_amount = models.FloatField(default=0)
    # Optional: last updated time
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Total Income: {self.total_amount} (Updated at {self.updated_at.strftime('%Y-%m-%d %H:%M')})"

    def save(self, *args, **kwargs):
        if self.total_amount < 0:
            self.total_amount = 0  # automatically set negative values to 0
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "TotalIncome"
        verbose_name_plural = "TotalIncomes"
        default_permissions = ()  # disable default English ones
        permissions = [
            ("view_totalIncome", "can view total income"),
        ]

class TotalExpenses(models.Model):
    total_amount = models.FloatField(default=0)
    # Optional: last updated time
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Total Income: {self.total_amount} (Updated at {self.updated_at.strftime('%Y-%m-%d %H:%M')})"

    def save(self, *args, **kwargs):
        if self.total_amount < 0:
            self.total_amount = 0  # automatically set negative values to 0
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "TotalExpenses"
        verbose_name_plural = "TotalExpensess"
        default_permissions = ()  # disable default English ones
        permissions = [
            ("view_totalexpenses", "can view total expenses"),
        ]

class OtherIncome(models.Model):
    date = models.CharField(max_length=14, blank=False)
    amount = models.FloatField()
    description = models.TextField()

    class Meta:
        verbose_name = "OtherIncome"
        verbose_name_plural = "OtherIncomes"
        default_permissions = ()  # disable default English ones
        permissions = [
            ("view_otherincome", "can view income records"),
        ]

class Expenses(models.Model):
    date = models.CharField(max_length=14, blank=False)
    amount = models.FloatField()
    description = models.TextField()

    class Meta:
        verbose_name = "Expenses"
        verbose_name_plural = "Expensess"
        default_permissions = ()  # disable default English ones
        permissions = [
            ("view_expenses", "can view expenses records"),
        ]