from django.db import models

# Create your models here.

class PraatScript(models.Model):
    name = models.CharField(max_length=512)
    # I haven't looked up how to reference local (server-side) files
    path = models.FileField(default="", blank=True, upload_to='praat_scripts')
    img  = models.ImageField(upload_to='praat_scripts_img', blank=True)
    # If no image is provided, the icon is used instead
    icon = models.CharField(max_length=4, blank=True)
    desc = models.TextField(max_length=32768)

    def __str__(self):
        return self.name
