"""Module to define db models related to the upload app."""
from django.db import models
from equestria.settings import BASE_DIR
import os
from django.contrib.auth.models import User


class File(models.Model):
    """Model representing user uploaded files in the database."""

    # owner = models.ForeignKey(
    #    User, to_field="username", on_delete=models.CASCADE
    # )
    owner = models.CharField(max_length=30)
    timestamp = models.DateTimeField(auto_now_add=True)
    path = models.FilePathField(path=os.path.join(BASE_DIR, "media/"))
    filetype = models.CharField(max_length=30)
    usage = models.CharField(max_length=30)
    project = models.CharField(max_length=10)

    def __str__(self):
        """Use name of script in admin display."""
        return self.owner + ", " + self.path

    class Meta:
        """
        Display configuration for admin pane.

        Display plural correctly.
        """

        verbose_name_plural = "Files"
