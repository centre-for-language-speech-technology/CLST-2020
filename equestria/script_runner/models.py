from django.db import models

# Create your models here.


class Script(models.Model):
    name = models.CharField(max_length=512)
    # I haven't looked up how to reference local (server-side) files
    path = models.FileField(default="", blank=True, upload_to='script')
    img = models.ImageField(upload_to='script_img', blank=True,
                            help_text='Thumbnail to symbolize script')
    # If no image is provided, the icon is used instead
    icon = models.CharField(max_length=4, blank=True,
                            help_text='FontAwesome glyph to show if image is unavailable')
    desc = models.TextField(max_length=32768)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Scripts"
