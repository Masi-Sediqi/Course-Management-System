from django.db import models

# Create your models here.

class Setting(models.Model):
    title = models.CharField(max_length=150, blank=False)
    logo = models.ImageField(upload_to="system_image/", blank=False)
    created_at = models.DateTimeField(auto_now_add=True)