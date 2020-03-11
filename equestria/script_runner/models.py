from django.db.models import *
from django.contrib.admin import StackedInline, ModelAdmin
from django import forms
from .constants import *

# Create your models here.


class Script(Model):
    name = CharField(max_length=512)
    # I haven't looked up how to reference local (server-side) files
    script_file = FilePathField(help_text="specify either a file to execute",
                                path="scripts/", blank=True)  # TODO change this
    command = CharField(help_text="or a command to execute",
                        max_length=2**10, blank=True)
    primary_output_file = FilePathField(help_text="The file to be used for live output",
                                        path="outputs/", blank=True)  # TODO change this
    output_file_or_directory = FilePathField(help_text="Additional outputs generated",
                                             path="outputs/", blank=True, allow_folders=True, recursive=False)  # TODO change this
    img = ImageField(upload_to='script_img', blank=True,
                     help_text='Thumbnail to symbolize script')
    # If no image is provided, the icon is used instead
    icon = CharField(max_length=4, blank=True,
                     help_text='FontAwesome glyph to show if image is unavailable')
    description = TextField(max_length=32768)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Scripts"


class Argument(Model):
    name = CharField(max_length=512)
    required = BooleanField(default=False)
    short_flag = CharField(max_length=16, blank=True)
    long_flag = CharField(max_length=512, blank=True)
    argument_choices = [
        (USER_SPECIFIED_FILE, "User specified file"),
        (USER_SPECIFIED_TEXT, "User specified string"),
        (USER_SPECIFIED_BOOL, "User specified boolean"),
        (USER_SPECIFIED_INT,  "User specified integer"),
    ]
    arg_type = IntegerField(choices=argument_choices)
    associated_script = ForeignKey(Script, on_delete=CASCADE, default=None)
    description = TextField(max_length=32768)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Arguments"


class OutputFile(Model):
    name = CharField(max_length=512)
    output_file = FilePathField(path="scripts/")  # TODO change this
    description = TextField(max_length=32768)
    associated_script = ForeignKey(Script, on_delete=CASCADE, default=None)

    def __str__(self):
        return self.name
