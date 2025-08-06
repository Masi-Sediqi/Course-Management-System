from django.db import models

# Create your models here.

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
    price = models.IntegerField(blank=False)
    description = models.TextField(blank=True)
    def __str__(self):
        return self.name