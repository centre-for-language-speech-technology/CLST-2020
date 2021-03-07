"""Module to define db models related to the upload app."""
import re
import secrets

from django.core.exceptions import ValidationError
from django.db.models import *
import clam.common.client
import clam.common.data
import clam.common.status
from clam.common import parameters as clam_parameters


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

    name = CharField(
        max_length=512,
        blank=False,
        null=False,
        help_text="The name of the script, used for " "identification only.",
    )

    hostname = URLField(
        blank=False,
        null=False,
        help_text="The full URL where the CLAM server for this Script is "
        "accessible.",
    )

    description = TextField(
        max_length=32768,
        blank=True,
        help_text="The description of this Script.",
    )

    username = CharField(
        max_length=200,
        blank=True,
        help_text="If the CLAM server requires authentication, enter the "
        "username for the authentication here.",
    )
    password = CharField(
        max_length=200,
        blank=True,
        help_text="If the CLAM server requires authentication, enter the "
        "password for the authentication here.",
    )

    @staticmethod
    def get_random_clam_id():
        """
        Get a random 32 bit string.

        :return: a random 32 bit string
        """
        return secrets.token_hex(32)

    @property
    def output_templates(self):
        """Get all output templates associated with this script."""
        return OutputTemplate.objects.filter(script=self)

    def refresh(self):
        """
        Save function to load profile data from CLAM.

        :return: super(Script, self).save()
        """
        # First contact CLAM to get the profile data
        random_token = Script.get_random_clam_id()
        try:
            clamclient = self.get_clam_server()
            clamclient.create(random_token)
            data = clamclient.get(random_token)
            clamclient.delete(random_token)
        except Exception as e:
            # If CLAM can't be reached, the credentials are most likely not valid
            raise ValidationError(
                "There was a problem contacting the CLAM server, did you enter the right username and"
                " password?"
            )

        # Remove the profiles that are now associated with this Script
        self.remove_corresponding_profiles()

        default_values = dict()
        for parameter in BaseParameter.objects.filter(
            corresponding_script=self
        ):
            default_key = parameter.get_default_value()
            if default_key is not None:
                default_values[parameter.name] = parameter.get_default_value()

        self.remove_corresponding_parameters()
        self.generate_parameters_from_clam_data(
            data.passparameters().keys(), data, default_values
        )

        # Create new profiles associated with this script
        for profile in data.profiles:
            self.create_templates_from_data(profile.input)

    def generate_parameters_from_clam_data(
        self, parameter_names, clam_data, default_values
    ):
        """
        Generate parameter objects from CLAM data and set default values for these objects.

        :param parameter_names: the names of the parameters to generate
        :param clam_data: the CLAM data
        :param default_values: a dictionary of (parameter_name, parameter_value) pairs with default values
        :return: None
        """
        for parameter_name in parameter_names:
            parameter = clam_data.parameter(parameter_name)
            type = BaseParameter.get_type(parameter)
            base_parameter = BaseParameter.objects.create(
                name=parameter_name, corresponding_script=self, type=type
            )
            if type == BaseParameter.BOOLEAN_TYPE:
                param = BooleanParameter.objects.create(base=base_parameter)
            elif type == BaseParameter.STATIC_TYPE:
                param = StaticParameter.objects.create(base=base_parameter)
            elif type == BaseParameter.STRING_TYPE:
                param = StringParameter.objects.create(base=base_parameter)
            elif type == BaseParameter.CHOICE_TYPE:
                param = ChoiceParameter.objects.create(base=base_parameter)
                choices = [x for _, x in parameter.choices]
                Choice.add_choices(choices, param)
            elif type == BaseParameter.TEXT_TYPE:
                param = TextParameter.objects.create(base=base_parameter)
            elif type == BaseParameter.INTEGER_TYPE:
                param = IntegerParameter.objects.create(base=base_parameter)
            elif type == BaseParameter.FLOAT_TYPE:
                param = FloatParameter.objects.create(base=base_parameter)
            else:
                param = None

            if parameter_name in default_values.keys() and param is not None:
                param.set_preset(default_values[parameter_name])

    def get_parameters(self):
        """
        Get all parameters for this script.

        :return: a QuerySet of BaseParameter objects corresponding to this script
        """
        return BaseParameter.objects.filter(corresponding_script=self)

    @property
    def variable_parameters(self):
        """Get variable parameters (parameters without a preset)."""
        return self.get_variable_parameters()

    def get_variable_parameters(self):
        """
        Get a list of all parameters without a preset.

        :return: a list of BaseParameter objects without a preset
        """
        parameters = self.get_parameters()
        variable_parameters = list()
        for parameter in parameters:
            if parameter.get_default_value() is None:
                variable_parameters.append(parameter)

        return variable_parameters

    def get_default_parameter_values(self):
        """
        Get a dictionary of (key, value) pairs for all default parameters.

        :return: a dictionary of (parameter_name, parameter_value) pairs for all default parameters with a preset
        """
        parameters = self.get_parameters()
        values = dict()
        for parameter in parameters:
            value = parameter.get_default_value()
            if value is not None:
                values[parameter.name] = value

        return values

    def construct_variable_parameter_values(self, parameter_dict):
        """
        Construct (key, value) pairs from a parameter dictionary.

        Also checks if the parameters in the dictionary exist for this script and if they have valid values.
        :param parameter_dict: a dictionary of (parameter_name, parameter_value) pairs
        :return: a dictionary of (parameter_name, parameter_value) pairs of parameters that have valid values and exist
        for this script
        """
        variable_dict = dict()
        for parameter_name, parameter_value in parameter_dict.items():
            try:
                parameter = BaseParameter.objects.get(
                    name=parameter_name, corresponding_script=self
                )
                value = parameter.get_corresponding_value(parameter_value)
                if value is not None:
                    variable_dict[parameter_name] = value
            except BaseParameter.DoesNotExist:
                pass
        return variable_dict

    def get_parameters_as_dict(self, preset_parameters=None):
        """
        Get all parameters as (key, value) pairs.

        :param preset_parameters: a dictionary of (parameter_name, parameter_value) pairs for parameters without a
        default value
        :return: a dictionary of (parameter_name, parameter_value) pairs including all default parameters with their
        values and the parameter presets in preset_parameters. If a parameter is in preset_parameters and has a default
        value the preset_parameters value is overwritten
        """
        if preset_parameters is None:
            preset_parameters = dict()

        default_parameters = self.get_default_parameter_values()
        variable_parameters = self.construct_variable_parameter_values(
            preset_parameters
        )

        return {**variable_parameters, **default_parameters}

    def get_unsatisfied_parameters(self, parameter_names):
        """
        Get all parameters without their name in parameter_names.

        :param parameter_names: a list of satisfied parameter names
        :return: a list of parameters without their names being in parameter_names
        """
        parameters = self.get_parameters()
        not_satisfied = list()
        for parameter in parameters:
            if parameter.name not in parameter_names:
                not_satisfied.append(parameter)

        return not_satisfied

    def create_templates_from_data(self, input_templates):
        """
        Create InputTemplate objects from CLAM input template data.

        :param input_templates: a list of CLAM input template objects
        :return: None
        """
        new_profile = Profile.objects.create(script=self)
        for input_template in input_templates:
            InputTemplate.objects.create(
                template_id=input_template.id,
                format=input_template.formatclass,
                label=input_template.label,
                extension=input_template.extension,
                optional=input_template.optional,
                unique=input_template.unique,
                accept_archive=input_template.acceptarchive,
                corresponding_profile=new_profile,
            )

    def __str__(self):
        """Use name of script in admin display."""
        return self.name

    def remove_corresponding_profiles(self):
        """
        Remove all profiles corresponding to this process.

        :return: None
        """
        Profile.objects.filter(script=self).delete()

    def remove_corresponding_parameters(self):
        """
        Remove all parameters corresponding to this process.

        :return: None
        """
        BaseParameter.objects.filter(corresponding_script=self).delete()

    def get_clam_server(self):
        """
        Get a CLAM server for handling this script.

        :return: a CLAMClient
        """
        if self.username != "" and self.password != "":
            return clam.common.client.CLAMClient(
                self.hostname, self.username, self.password, basicauth=True
            )
        else:
            return clam.common.client.CLAMClient(self.hostname)

    class Meta:
        """
        Display configuration for admin pane.

        Order admin list alphabetically by name.
        Display plural correctly.
        """

        ordering = ["name"]
        verbose_name_plural = "Scripts"


class Profile(Model):
    """
    Database model for profiles.

    A profile is a set of InputTemplates (possibly more later on)
    Attributes:
        script                 The script associated with this profile.
    """

    name = CharField(
        max_length=1024,
        null=True,
        blank=True,
        help_text="Optional name, will be showed instead of profile number.",
    )
    script = ForeignKey(
        Script,
        related_name="profiles",
        on_delete=CASCADE,
        null=False,
        blank=False,
        help_text="The Script this Profile belongs to.",
    )

    def __str__(self):
        """
        Use identifier in admin pane.

        :return: string including the identifier of this object
        """
        if self.name:
            return self.name
        else:
            return "Profile {}".format(self.pk)

    @property
    def templates(self):
        """
        Get the templates corresponding to this profile.

        :return: a QuerySet of templates corresponding to this profile
        """
        return InputTemplate.objects.filter(corresponding_profile=self)

    class Meta:
        """
        Display configuration for admin pane.

        Order admin list by id.
        Display plural correctly.
        """

        ordering = ["id"]
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"


class InputTemplate(Model):
    """
    Database model for input templates provided by the CLAM server.

    An input template is provided by CLAM and puts restrictions on what types of input files can be uploaded
    Attributes:
        template_id             The identifier of this input template in the CLAM server.
        format                  The format of this input template as a CLAM format.
        mime                    The accepted mime type
        label                   The label of this input template.
        extension               The accepted extension by this input template.
        optional                Whether or not this template is optional before starting the associated script.
        unique                  Whether or not there is only one of these files per process. If this equals True a file
                                must first be deleted before overwriting it on the CLAM server.
        accept_archive          Whether or not this template accepts archive files.
        corresponding_profile   The corresponding profile of this input template.
    """

    template_id = CharField(
        max_length=1024,
        help_text="Template ID as mirrored from the CLAM server.",
    )
    format = CharField(
        max_length=1024,
        help_text="CLAM format as mirrored from the CLAM server.",
    )
    label = CharField(
        max_length=1024,
        help_text="Label used for describing what files to select for this Input "
        "template",
    )
    mime = CharField(
        max_length=1024,
        default="text/plain",
        help_text="The mime class used for files selected for "
        "this Input template.",
    )
    extension = CharField(
        max_length=32,
        help_text="The preferred extension a file should have when it is selected "
        "to be used for this Input template.",
    )
    optional = BooleanField(
        help_text="Whether or not this Input template is optional."
    )
    unique = BooleanField(
        help_text="Whether or not multiple files could be uploaded for this Input template."
    )
    accept_archive = BooleanField(
        help_text="Whether or not this Input template accepts archives."
    )
    corresponding_profile = ForeignKey(
        Profile,
        related_name="input_templates",
        on_delete=CASCADE,
        null=False,
        blank=False,
        help_text="The Profile associated with this Input template.",
    )

    def __str__(self):
        """
        Cast this object to a string.

        :return: this object formatted in string format
        """
        unique = "Unique" if self.unique else ""
        if unique:
            optional = " optional" if self.optional else ""
        else:
            optional = "Optional" if self.optional else ""
        if self.unique or self.optional:
            return "{}{} file with extension {} for script {}".format(
                unique,
                optional,
                self.extension,
                self.corresponding_profile.script,
            )
        else:
            return "File with extension {} for script {}".format(
                self.extension, self.corresponding_profile.script
            )

    class Meta:
        """
        Display configuration for admin pane.

        Order admin list by id.
        Display plural correctly.
        """

        ordering = ["id"]
        verbose_name = "Input template"
        verbose_name_plural = "Input templates"


class OutputTemplate(Model):
    """
    OutputTemplate model.

    Output templates are used when a Process finishes running. By default, no files that a Process outputs are copied
    over to the Project. Only files with file names that match an Output template will be copied over to the Project
    directory.
    """

    script = ForeignKey(
        Script,
        on_delete=CASCADE,
        null=False,
        blank=False,
        help_text="The Script corresponding to" " this Output template.",
    )
    regex = CharField(
        max_length=1024,
        null=False,
        blank=False,
        help_text="The regular expression to use when "
        "matching output file names of processes. "
        "Matching output files will be copied over to"
        " the Project directory.",
    )

    def __init__(self, *args, **kwargs):
        """Initialise OutputTemplate model."""
        super().__init__(*args, **kwargs)
        self._regex = re.compile(self.regex)

    @staticmethod
    def match_any(filename, output_templates):
        """Check if any of the output templates matches filename."""
        for output_template in output_templates:
            if output_template.match(filename):
                return True
        return False

    @staticmethod
    def match_all(filename, output_templates):
        """Check if all of the output templates matches filename."""
        for output_template in output_templates:
            if not output_template.match(filename):
                return False
        return True

    def match(self, filename):
        """Check if this output template matches filename."""
        return self._regex.match(filename)


class BaseParameter(Model):
    """Base model for a parameter object."""

    BOOLEAN_TYPE = 0
    STATIC_TYPE = 1
    STRING_TYPE = 2
    CHOICE_TYPE = 3
    TEXT_TYPE = 4
    INTEGER_TYPE = 5
    FLOAT_TYPE = 6

    TYPES = (
        (BOOLEAN_TYPE, "Boolean"),
        (STATIC_TYPE, "Static"),
        (STRING_TYPE, "String"),
        (CHOICE_TYPE, "Choice"),
        (TEXT_TYPE, "Text"),
        (INTEGER_TYPE, "Integer"),
        (FLOAT_TYPE, "Float"),
    )

    name = CharField(
        max_length=1024,
        help_text="Identifier for a Base Parameter. This is set automatically when "
        "synchronizing with a CLAM server.",
    )
    corresponding_script = ForeignKey(
        Script,
        related_name="parameters",
        on_delete=CASCADE,
        null=False,
        blank=False,
        help_text="The Script this Parameter belongs to.",
    )
    preset = BooleanField(
        default=False,
        help_text="Whether or not this Parameter can be set by Users themselves. When "
        "this is False, Users will be able to set this Parameter themselves"
        " when running Processes. When this is True a value for this "
        "parameter should be specified in one of the fields below.",
    )
    type = IntegerField(
        choices=TYPES,
        help_text="Indicates what the type is of this Parameter. When specifying a "
        "preset you should enter the value of the Parameter within the right "
        "typed field below.",
    )

    @staticmethod
    def get_type(parameter):
        """
        Get the type of a CLAM parameter.

        :param parameter: the CLAM parameter object
        :return: the type of the CLAM parameter in BaseParameter.TYPES types
        """
        if parameter.__class__ == clam_parameters.BooleanParameter:
            return BaseParameter.BOOLEAN_TYPE
        elif parameter.__class__ == clam_parameters.StaticParameter:
            return BaseParameter.STATIC_TYPE
        elif parameter.__class__ == clam_parameters.StringParameter:
            return BaseParameter.STRING_TYPE
        elif parameter.__class__ == clam_parameters.ChoiceParameter:
            return BaseParameter.CHOICE_TYPE
        elif parameter.__class__ == clam_parameters.TextParameter:
            return BaseParameter.TEXT_TYPE
        elif parameter.__class__ == clam_parameters.IntegerParameter:
            return BaseParameter.INTEGER_TYPE
        elif parameter.__class__ == clam_parameters.FloatParameter:
            return BaseParameter.FLOAT_TYPE
        else:
            raise TypeError("Type of parameter {} unknown".format(parameter))

    def get_typed_parameter(self):
        """
        Get the corresponding typed parameter for this object.

        :return: a typed parameter object corresponding to this object
        """
        try:
            if self.type == self.BOOLEAN_TYPE:
                return BooleanParameter.objects.get(base=self)
            elif self.type == self.STATIC_TYPE:
                return StaticParameter.objects.get(base=self)
            elif self.type == self.STRING_TYPE:
                return StringParameter.objects.get(base=self)
            elif self.type == self.CHOICE_TYPE:
                return ChoiceParameter.objects.get(base=self)
            elif self.type == self.TEXT_TYPE:
                return TextParameter.objects.get(base=self)
            elif self.type == self.INTEGER_TYPE:
                return IntegerParameter.objects.get(base=self)
            elif self.type == self.FLOAT_TYPE:
                return FloatParameter.objects.get(base=self)
            else:
                return None
        except (
            BooleanParameter.DoesNotExist,
            StaticParameter.DoesNotExist,
            StringParameter.DoesNotExist,
            ChoiceParameter.DoesNotExist,
            TextParameter.DoesNotExist,
            IntegerParameter.DoesNotExist,
            FloatParameter.DoesNotExist,
        ) as e:
            return None

    def get_default_value(self):
        """
        Get the default value of a parameter.

        :return: the default value of a parameter, None if the default value is not set
        """
        if not self.preset:
            return None
        else:
            typed_parameter = self.get_typed_parameter()
            if typed_parameter is not None:
                return typed_parameter.get_value()
            else:
                return None

    @property
    def value(self):
        """
        Get the default value of a parameter.

        :return: the default value of a parameter, None if the default value is not set
        """
        if not self.preset:
            return None
        else:
            typed_parameter = self.get_typed_parameter()
            if typed_parameter is not None:
                return typed_parameter.get_value()
            else:
                return None

    def get_corresponding_value(self, value):
        """
        Get and check a value for this parameter.

        This function receives a value and checks if it is of the same type as this parameter. If it is not, this
        function will return None.
        :param value: the value for this parameter, for choice types the value can either be the private key or a
        Choice object
        :return: the value for this parameter if the instance of the value is matching the parameter type. For
        choice types the value is also checked against the choices and the value of the corresponding choice is
        returned, None is returned if the type of the value does not match the type of the parameter
        """
        typed_parameter = self.get_typed_parameter()
        if typed_parameter is None:
            raise BaseParameter.ParameterException("Typed parameter not found.")
        return typed_parameter.get_corresponding_value(value)

    def __str__(self):
        """
        Convert this model to string.

        :return: the name of this model and the private key
        """
        return "{} ({})".format(self.name, self.pk)

    class ParameterException(Exception):
        """Exception to be thrown when a parameter error occurs."""

        pass

    class Meta:
        """Meta class."""

        verbose_name_plural = "Parameters"
        verbose_name = "Parameter"
        unique_together = ("name", "corresponding_script")


class BooleanParameter(Model):
    """Parameter for boolean values."""

    base = OneToOneField(
        BaseParameter,
        on_delete=CASCADE,
        null=False,
        blank=False,
        help_text="The Base parameter this typed parameter " "belongs to.",
    )
    value = BooleanField(
        default=False,
        null=True,
        blank=True,
        help_text="The boolean value for this parameter.",
    )

    def get_value(self):
        """
        Get the current value.

        :return: the current value of this parameter
        """
        return self.value

    def get_corresponding_value(self, value):
        """
        Check if the value is valid for this parameter.

        :param value: the value to check
        :return: None if the value is not valid, the value otherwise
        """
        if isinstance(value, bool):
            return value
        else:
            return None

    def set_preset(self, value):
        """
        Set a preset for this parameter.

        :param value: the value to set the preset to
        :return: None
        """
        if isinstance(value, bool):
            self.base.preset = True
            self.base.save()
            self.value = value
            self.save()


class StaticParameter(Model):
    """Parameter for static values."""

    base = OneToOneField(
        BaseParameter,
        on_delete=CASCADE,
        null=False,
        blank=False,
        help_text="The Base parameter this typed parameter " "belongs to.",
    )
    value = CharField(
        max_length=2048,
        null=True,
        blank=True,
        help_text="The static value for this parameter.",
    )

    def get_value(self):
        """
        Get the current value.

        :return: the current value of this parameter
        """
        return self.value

    def get_corresponding_value(self, value):
        """
        Check if the value is valid for this parameter.

        :param value: the value to check
        :return: the value of this parameter (as this is a static parameter which can not be set)
        """
        return self.value

    def set_preset(self, value):
        """
        Set a preset for this parameter.

        :param value: the value to set the preset to
        :return: None
        """
        if isinstance(value, str):
            self.base.preset = True
            self.base.save()
            self.value = value
            self.save()


class StringParameter(Model):
    """Parameter for string values."""

    base = OneToOneField(
        BaseParameter,
        on_delete=CASCADE,
        null=False,
        blank=False,
        help_text="The Base parameter this typed parameter " "belongs to.",
    )
    value = CharField(
        max_length=2048,
        null=True,
        blank=True,
        help_text="The string value for this parameter.",
    )

    def get_value(self):
        """
        Get the current value.

        :return: the current value of this parameter
        """
        return self.value

    def get_corresponding_value(self, value):
        """
        Check if the value is valid for this parameter.

        :param value: the value to check
        :return: None if the value is not valid, the value otherwise
        """
        if isinstance(value, str):
            return value
        else:
            return None

    def set_preset(self, value):
        """
        Set a preset for this parameter.

        :param value: the value to set the preset to
        :return: None
        """
        if isinstance(value, str):
            self.base.preset = True
            self.base.save()
            self.value = value
            self.save()


class Choice(Model):
    """Model for choices in ChoiceParameter."""

    corresponding_choice_parameter = ForeignKey(
        "ChoiceParameter",
        on_delete=CASCADE,
        null=False,
        blank=False,
        help_text="The Choice parameter the Choice " "belongs to.",
    )
    value = CharField(max_length=2048, help_text="The value of a choice.")

    def get_value(self):
        """
        Get the current value.

        :return: the current value of this parameter
        """
        return self.value

    def __str__(self):
        """
        Convert this object to a string.

        :return: the value of this object
        """
        return self.value

    @staticmethod
    def add_choices(choices, choice_parameter):
        """
        Add choices to a choice parameter.

        :param choices: the choices to add as a list of values
        :param choice_parameter: the choice parameter to add the choices to
        :return: None
        """
        for value in choices:
            Choice.objects.create(
                corresponding_choice_parameter=choice_parameter, value=value
            )


class ChoiceParameter(Model):
    """Parameter for choice values."""

    base = OneToOneField(
        BaseParameter,
        on_delete=CASCADE,
        null=False,
        blank=False,
        help_text="The Base parameter this typed parameter " "belongs to.",
    )
    value = ForeignKey(
        Choice,
        on_delete=SET_NULL,
        null=True,
        blank=True,
        help_text="The choice value for this " "parameter.",
    )

    def get_value(self):
        """
        Get the current value.

        :return: the current value of this parameter
        """
        return self.value.get_value()

    def get_corresponding_value(self, value):
        """
        Check if the value is valid for this parameter.

        :param value: the value to check, can be either a Choice or a pk of a Choice
        :return: None if the value is not valid, the value of the corresponding Choice object otherwise
        """
        if isinstance(value, Choice):
            choice = value
        else:
            try:
                choice = Choice.objects.get(pk=value)
            except Choice.DoesNotExist:
                return None
        if choice.corresponding_choice_parameter == self:
            return choice.value
        else:
            return None

    def remove_corresponding_choices(self):
        """
        Remove the choices corresponding to this model from the database.

        :return: None
        """
        choices = Choice.objects.filter(corresponding_choice_parameter=self)
        for choice in choices:
            choice.delete()

    def get_available_choices(self):
        """Get Choice object corresponding to this ChoiceParameter."""
        return Choice.objects.filter(corresponding_choice_parameter=self)

    def set_preset(self, value):
        """
        Set a preset for this parameter.

        :param value: the value to set the preset to
        :return: None
        """
        if isinstance(value, str):
            try:
                choice = Choice.objects.get(
                    corresponding_choice_parameter=self, value=value
                )
                self.value = choice
                self.save()
                self.base.preset = True
                self.base.save()
            except (Choice.MultipleObjectsReturned, Choice.DoesNotExist):
                pass

    def __str__(self):
        """Convert this object to string."""
        if self.base is not None:
            return "Choice parameter for {}".format(self.base)
        else:
            return "Choice parameter ({})".format(self.pk)


class TextParameter(Model):
    """Parameter for text values."""

    base = OneToOneField(
        BaseParameter,
        on_delete=CASCADE,
        null=False,
        blank=False,
        help_text="The Base parameter this typed parameter " "belongs to.",
    )
    value = TextField(
        null=True, blank=True, help_text="The text value for this parameter."
    )

    def get_value(self):
        """
        Get the current value.

        :return: the current value of this parameter
        """
        return self.value

    def get_corresponding_value(self, value):
        """
        Check if the value is valid for this parameter.

        :param value: the value to check
        :return: None if the value is not valid, the value otherwise
        """
        if isinstance(value, str):
            return value
        else:
            return None

    def set_preset(self, value):
        """
        Set a preset for this parameter.

        :param value: the value to set the preset to
        :return: None
        """
        if isinstance(value, str):
            self.base.preset = True
            self.base.save()
            self.value = value
            self.save()


class IntegerParameter(Model):
    """Parameter for integer values."""

    base = OneToOneField(
        BaseParameter,
        on_delete=CASCADE,
        null=False,
        blank=False,
        help_text="The Base parameter this typed parameter " "belongs to.",
    )
    value = IntegerField(
        null=True, blank=True, help_text="The integer value for this parameter."
    )

    def get_value(self):
        """
        Get the current value.

        :return: the current value of this parameter
        """
        return self.value

    def get_corresponding_value(self, value):
        """
        Check if the value is valid for this parameter.

        :param value: the value to check
        :return: None if the value is not valid, the value otherwise
        """
        if isinstance(value, int):
            return value
        else:
            return None

    def set_preset(self, value):
        """
        Set a preset for this parameter.

        :param value: the value to set the preset to
        :return: None
        """
        if isinstance(value, int):
            self.base.preset = True
            self.base.save()
            self.value = value
            self.save()


class FloatParameter(Model):
    """Parameter for float values."""

    base = OneToOneField(
        BaseParameter,
        on_delete=CASCADE,
        null=False,
        blank=False,
        help_text="The Base parameter this typed parameter " "belongs to.",
    )
    value = FloatField(
        null=True, blank=True, help_text="The float value for this parameter."
    )

    def get_value(self):
        """
        Get the current value.

        :return: the current value of this parameter
        """
        return self.value

    def get_corresponding_value(self, value):
        """
        Check if the value is valid for this parameter.

        :param value: the value to check
        :return: None if the value is not valid, the value otherwise
        """
        if isinstance(value, float):
            return value
        else:
            return None

    def set_preset(self, value):
        """
        Set a preset for this parameter.

        :param value: the value to set the preset to
        :return: None
        """
        if isinstance(value, float):
            self.base.preset = True
            self.base.save()
            self.value = value
            self.save()
