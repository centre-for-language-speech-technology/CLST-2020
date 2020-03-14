from django.db.models import *
from .constants import *

# Create your models here.


class Script(Model):
    """
    Database model for scripts.

    Attributes:
        name                          Name of the script. Used for identification only, can be anything.
        script_file                   The file to execute.
        command                       Alternatively if script_file is None, the command to execute.
        primary_output_file           The file containing output of the script that should be displayed to the user.
        output_file_or_directory      The folder containing all output files.
                                      May be a single file if no such folder exists.
        img                           The image to display in script selection screens.
        icon                          If image is None, letters or FontAwesome icon to display instead.
        description                   Documentation of the purpose of the script.
    """

    name = CharField(max_length=512)
    # I haven't looked up how to reference local (server-side) files
    script_file = FilePathField(
        help_text="specify either a file to execute",
        # TODO: change this path
        path="./",
        blank=True,
    )  # TODO change this
    command = CharField(
        help_text="or a command to execute", max_length=2 ** 10, blank=True
    )
    primary_output_file = FilePathField(
        help_text="The file to be used for live output", path="./", blank=True,
    )  # TODO change this
    output_file_or_directory = FilePathField(
        help_text="Additional outputs generated",
        path="./",
        blank=True,
        allow_folders=True,
        recursive=False,
    )  # TODO change this
    img = ImageField(
        upload_to="script_img",
        blank=True,
        help_text="Thumbnail to symbolize script",
    )
    # If no image is provided, the icon is used instead
    icon = CharField(
        max_length=4,
        blank=True,
        help_text="FontAwesome glyph to show if image is unavailable",
    )
    description = TextField(max_length=32768)

    def __str__(self):
        """Use name of script in admin display."""
        return self.name

    class Meta:
        """
        Display configuration for admin pane.

        Order admin list alphabetically by name.
        Display plural correctly.
        """

        ordering = ["name"]
        verbose_name_plural = "Scripts"


class Argument(Model):
    """
    Database model for scripts.

    Attributes:
        name                          Name of the command line argument. 
                                      Used for identification only, can be anything.
        required                      Whether the argument is optional or needs to be filled out.
                                      If not required, booleans default to false.
        short_flag                    Short flag (e.g. -f) of argument. Preceding dash not implicit.
        long_flag                     Long flag (e.g. --force) of argument. Preceding dashes not implicit.
        arg_type                      Type of value to be supplied by user. May be one of:
            file                      Any file uploaded by the user. 
            text                      A string written by the user.
            bool                      A checkbox that may be true or false.
            int                       An integer (may be negative).
        associated_script             Script object the argument belongs to.
        description                   Documentation of the purpose of the argument.
    """

    name = CharField(max_length=512)
    required = BooleanField(default=False)
    short_flag = CharField(max_length=16, blank=True)
    long_flag = CharField(max_length=512, blank=True)
    argument_choices = [
        (USER_SPECIFIED_FILE, "User specified file"),
        (USER_SPECIFIED_TEXT, "User specified string"),
        (USER_SPECIFIED_BOOL, "User specified boolean"),
        (USER_SPECIFIED_INT, "User specified integer"),
    ]
    arg_type = IntegerField(choices=argument_choices)
    associated_script = ForeignKey(Script, on_delete=CASCADE, default=None)
    description = TextField(max_length=32768)

    def __str__(self):
        """Use name of argument in admin display."""
        return self.name

    class Meta:
        """
        Display configuration for admin pane.

        Order admin list alphabetically by name.
        Display plural correctly.
        """

        ordering = ["name"]
        verbose_name_plural = "Arguments"


class OutputFile(Model):
    """
    Database model for output files of scripts. Not yet used.

    TODO: Decide whether to use primary_output_file or this.

    Attributes:
        name                          Name of the file. 
                                      Used for identification only, can be anything.
        output_file                   Output file on disk.
        description                   Documentation of the purpose/content of the file.
        associated_script             Script object the file belongs to.
    """

    name = CharField(max_length=512)
    output_file = FilePathField(path="./")  # TODO change this
    description = TextField(max_length=32768)
    associated_script = ForeignKey(Script, on_delete=CASCADE, default=None)

    def __str__(self):
        """Use name of output file in admin display."""
        return self.name
