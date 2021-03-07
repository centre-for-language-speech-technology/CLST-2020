from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Project
import shutil


@receiver(post_delete, sender=Project)
def delete_project_folder(sender, instance, **kwargs):
    """Delete project folder upon destroy."""
    shutil.rmtree(instance.absolute_path)
