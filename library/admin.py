from django.contrib import admin

from library.models import StationeryCategory, StationeryItem

# Register your models here.

admin.site.register(StationeryCategory)
admin.site.register(StationeryItem)