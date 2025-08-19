from django.db import models

# Create your models here.

class Subjects(models.Model):
    name = models.CharField(max_length=120)
    create = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name