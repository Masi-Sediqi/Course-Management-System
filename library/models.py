from django.db import models

class StationeryCategory(models.Model):
    name = models.CharField(max_length=50, blank=False)

    def __str__(self):
        return self.name

class StationeryItem(models.Model):
    name = models.CharField(max_length=100, blank=False)
    category = models.ForeignKey(StationeryCategory, on_delete=models.SET_NULL, null=True)
    price = models.IntegerField(blank=False)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Books(models.Model):
    name = models.CharField(max_length=115, blank=False)
    number_of_book = models.IntegerField(blank=False)
    price = models.IntegerField(blank=False)
    paid_price = models.IntegerField()
    description = models.TextField(blank=True)
    def __str__(self):
        return self.name

class Total_Stationery_Loan(models.Model):
    total_amount = models.FloatField()
    created = models.DateField(auto_now_add=True)