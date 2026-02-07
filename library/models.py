from django.db import models
from home.models import suppliers
import jdatetime

class Item(models.Model):

    date = models.CharField(max_length=13)
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.date: 
            self.date = jdatetime.date.today().strftime("%Y/%m/%d")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}"


class Purchase(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='purchases')
    date = models.CharField(max_length=13)
    number = models.IntegerField()
    per_price = models.FloatField()
    total_price = models.FloatField()
    paid_price = models.FloatField()
    remain_price = models.FloatField()
    supplier = models.ForeignKey(suppliers, on_delete=models.CASCADE)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.item.name} - {self.number} pcs on {self.date}"


class TotalItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='total')
    total_item = models.IntegerField(default=0)
    total_remain_item = models.IntegerField(default=0)
    per_price = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.item.name} - {self.total_item} pcs"