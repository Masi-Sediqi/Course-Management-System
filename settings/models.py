from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from datetime import datetime

# Create your models here.

class Setting(models.Model):
    title = models.CharField(max_length=150, blank=False)
    logo = models.ImageField(upload_to="system_image/", blank=False)
    created_at = models.DateTimeField(auto_now_add=True)

class Notification(models.Model):

    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Date fields
    notification_date = models.CharField(max_length=15)  # Store as string
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Read status
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Generic foreign key to any model
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    

    class Meta:
        ordering = ['-is_read', '-created_at']
    
    def __str__(self):
        return f" - {self.title}"
    
    def mark_as_read(self):
        self.is_read = True
        self.read_at = timezone.now()
        self.save()
    
    def mark_as_unread(self):
        self.is_read = False
        self.read_at = None
        self.save()


from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class SystemBackup(models.Model):
    created_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="system_backups"
    )
    backup_file = models.FileField(
        upload_to='system_backups/',
        null=True,
        blank=True
    )
    file_size = models.BigIntegerField(null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    folder_name = models.CharField(max_length=200, blank=True, null=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Backup #{self.id} - {self.created_at}"
