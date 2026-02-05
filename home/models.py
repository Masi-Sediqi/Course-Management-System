from django.db import models
import jdatetime
# Create your models here.

class suppliers(models.Model):
    date = models.CharField(max_length=15)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.date:
            # set date only when creating new record
            self.date = jdatetime.date.today().strftime("%Y/%m/%d")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
class Remaining(models.Model):
    supplier = models.ForeignKey(suppliers, on_delete=models.CASCADE)
    total_amount = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.total_amount < 0:
            self.total_amount = 0
        super().save(*args, **kwargs)