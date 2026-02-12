from django.db import models
import jdatetime
from django.conf import settings
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
    
class ColculationWithSupplier(models.Model):
    COL_TYPE = [
        ('بیلانس', 'بیلانس'),
        ('پرداخت', 'پرداخت'),
        ('خریداری', 'خریداری'),
    ]
    supplier = models.ForeignKey(suppliers, on_delete=models.CASCADE)
    colculation_type = models.CharField(max_length=100, choices=COL_TYPE, blank=True, null=True)
    total_price = models.FloatField(default=0, blank=True, null=True)
    paid_price = models.FloatField(default=0, blank=True, null=True)
    remain_price = models.FloatField(default=0, blank=True, null=True)
    remain_balance = models.FloatField(blank=True,null=True,verbose_name='بیلانس باقی‌مانده')
    purchase_item = models.ForeignKey('library.Purchase', on_delete=models.CASCADE, blank=True, null=True)
    date = models.CharField(max_length=14, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class SystemLog(models.Model):
    section = models.CharField(max_length=100)
    action = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    def __str__(self):
        return f"{self.action} at {self.timestamp}"