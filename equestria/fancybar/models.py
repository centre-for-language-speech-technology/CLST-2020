from django.db import models

# Create your models here.


class PraatScripts(models.Model):
    """Legacy database model for praat scripts. To be deleted, do not use."""

    name = models.CharField(max_length=512)
    # I haven't looked up how to reference local (server-side) files
    path = models.FileField(default="", blank=True, upload_to="praat_scripts")
    img = models.ImageField(upload_to="praat_scripts_img", blank=True)
    # If no image is provided, the icon is used instead
    icon = models.CharField(max_length=4, blank=True)
    desc = models.TextField(max_length=32768)

    def __str__(self):
        """Use name of script in admin display."""
        return self.name

    class Meta:
        """
        Display configuration for admin pane.

        Display plural correctly.
        """

        verbose_name_plural = "Praat scripts"
