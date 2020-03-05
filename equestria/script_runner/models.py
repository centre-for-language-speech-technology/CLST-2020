from django.db.models import *
from django.contrib.admin import StackedInline, ModelAdmin

# Create your models here.


class Script(Model):
    name = CharField(max_length=512)
    # I haven't looked up how to reference local (server-side) files
    path = FileField(default="", blank=True, upload_to='script')
    img = ImageField(upload_to='script_img', blank=True,
                     help_text='Thumbnail to symbolize script')
    # If no image is provided, the icon is used instead
    icon = CharField(max_length=4, blank=True,
                     help_text='FontAwesome glyph to show if image is unavailable')
    desc = TextField(max_length=32768)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Scripts"


class Argument(Model):
    name = CharField(max_length=512)
    associated_script = ForeignKey(Script, on_delete=CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Arguments"
