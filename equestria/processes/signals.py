from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Process
import shutil


@receiver(post_delete, sender=Process)
def delete_process_folder(sender, instance, **kwargs):
    """Delete process folder upon destroy."""
    shutil.rmtree(instance.absolute_process_folder)
