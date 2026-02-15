# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from .models import Student_fess_info
from settings.models import Notification

@receiver(post_save, sender=Student_fess_info)
def create_fee_notification(sender, instance, created, **kwargs):
    if created and instance.end_date:
        Notification.objects.create(
            title="موعد پرداخت فیس شاگرد",
            message=f"موعد پرداخت شاگرد {instance.student.first_name} نزدیک است",
            notification_date=instance.end_date,   # save end_date
            content_type=ContentType.objects.get_for_model(instance),
            object_id=instance.id,
        )