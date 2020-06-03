"""Module to define db models related to the upload app."""
import shutil

import pytz
from django.core.exceptions import ValidationError
from django.db.models import *
import clam.common.client
import clam.common.data
import clam.common.status
import xml.etree.ElementTree as ET
import datetime
import logging
from django.conf import settings
import os
import secrets
from django.contrib.auth import get_user_model
import zipfile
from .services import zip_dir
from .tasks import update_script

# Create your models here.

STATUS_CREATED = 0
STATUS_UPLOADING = 1
STATUS_RUNNING = 2
STATUS_WAITING = 3
STATUS_DOWNLOADING = 4
STATUS_FINISHED = 5
STATUS_ERROR = -1
STATUS_ERROR_DOWNLOAD = -2

STATUS = (
    (STATUS_CREATED, "Created"),
    (STATUS_UPLOADING, "Uploading files to CLAM"),
    (STATUS_RUNNING, "Running"),
    (STATUS_WAITING, "Waiting for download from CLAM"),
    (STATUS_DOWNLOADING, "Downloading files from CLAM"),
    (STATUS_FINISHED, "Finished"),
    (STATUS_ERROR, "Error"),
    (STATUS_ERROR_DOWNLOAD, "Error while downloading files from CLAM"),
)

User = get_user_model()


def user_data_folder_path():
    """
    Get the user data folder path.

    This function exists because otherwise the migrations for the Django Process and Project object
    will not display the correct path
    :return: settings.USER_DATA_FOLDER
    """
    return settings.USER_DATA_FOLDER


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

    name = CharField(max_length=512, blank=False, null=False)

    hostname = URLField(blank=False, null=False)

    description = TextField(max_length=32768, blank=True)

    username = CharField(max_length=200, blank=True)
    password = CharField(max_length=200, blank=True)

    def refresh(self):
        """
        Save function to load profile data from CLAM.

        :param args: arguments
        :param kwargs: keyword arguments
        :return: super(Script, self).save()
        """
        # First contact CLAM to get the profile data
        random_token = Process.get_random_clam_id()
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
        profiles = Profile.objects.filter(script=self)
        for profile in profiles:
            profile.remove_corresponding_templates()
            profile.delete()

    def remove_corresponding_parameters(self):
        """
        Remove all parameters corresponding to this process.

        :return: None
        """
        parameters = BaseParameter.objects.filter(corresponding_script=self)
        for parameter in parameters:
            parameter.remove_corresponding_presets()
            parameter.delete()

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

    def get_valid_profiles(self, folder):
        """
        Get the profiles for which the current files meet the requirements.

        :param folder: the folder to check for files
        :return:
        """
        profiles = Profile.objects.filter(script=self)
        valid_profiles = []

        for p in profiles:
            if p.is_valid(folder):
                valid_profiles.append(p)
        return valid_profiles

    class Meta:
        """
        Display configuration for admin pane.

        Order admin list alphabetically by name.
        Display plural correctly.
        """

        ordering = ["name"]
        verbose_name_plural = "Scripts"


class Process(Model):
    """
    Database model for processes in CLAM.

    Attributes:
        name                          Name of the process.
                                      Used for identification only, can be anything.
        clam_id                       Identification number given by CLAM.
        output_path                   Path to the primary output file (e.g. output/error.log)
    """

    OUTPUT_FOLDER_NAME = "output"

    script = ForeignKey(Script, on_delete=SET_NULL, blank=False, null=True)
    clam_id = CharField(max_length=256, null=True, default=None)
    status = IntegerField(choices=STATUS, default=0)
    folder = FilePathField(
        allow_folders=True, allow_files=False, path=user_data_folder_path
    )

    def __str__(self):
        """Convert this object to string."""
        return "Process for {} ({})".format(self.script, STATUS[self.status][1])

    @staticmethod
    def get_random_clam_id():
        """
        Get a random 32 bit string.

        :return: a random 32 bit string
        """
        return secrets.token_hex(32)

    def update_log_messages_from_xml(self, xml_data):
        """
        Update the log messages of this process from the CLAM xml data.

        :param xml_data: the XML data send by CLAM including a <status> tag with an arbitrary amount of <log> tags
        :return: None
        """
        try:
            # The clamclient does not have a way to retrieve the log messages so we will do it ourselves.
            xml = ET.fromstring(xml_data)
            for index, item in enumerate(
                reversed(list(xml.find("status").iter("log")))
            ):
                time = Process.parse_time_string(item.attrib["time"])
                if not LogMessage.objects.filter(
                    time=time, message=item.text, process=self, index=index
                ).exists():
                    LogMessage.objects.create(
                        time=time, message=item.text, process=self, index=index
                    )
        except Exception as e:
            logging.error(
                "Failed to parse XML response from CLAM server. Error: {}".format(
                    e
                )
            )

    @staticmethod
    def parse_time_string(time):
        """
        Parse the time string that CLAM passes.

        :param time: the time string from CLAM
        :return: a timezone aware datetime object, None when a ValueError was encountered
        """
        try:
            tz = pytz.timezone(settings.TIME_ZONE)
            return tz.localize(
                datetime.datetime.strptime(time, "%d/%b/%Y %H:%M:%S")
            )
        except ValueError:
            return None

    @property
    def output_folder(self):
        """
        Get an absolute path to the output folder.

        :return: the absolute path to the output folder
        """
        return os.path.join(self.folder, self.OUTPUT_FOLDER_NAME)

    def set_status(self, status):
        """
        Set the status for this process and save it to the Database.

        :param status: the status to set for this process
        :return: None
        """
        self.status = status
        self.save()

    def set_clam_id(self, clam_id):
        """
        Set the CLAM id for this process and save it to the Database.

        :param clam_id: the CLAM id to set for this process
        :return: None
        """
        self.clam_id = clam_id
        self.save()

    def start_safe(self, profile, parameter_values=None):
        """
        Start uploading files to CLAM and start the CLAM server in a safe way.

        Actually only executes the start() method and runs the cleanup() method when an exception is raised.
        :param profile: the profile to start this process with
        :param parameter_values: a dictionary of (key, value) pairs with the parameter values to fill in, only
        overwrites variable parameters
        :return: True when the process was started, False otherwise, raises a ValueError if there was an error with the
        input templates, raises an Exception if there was an error when uploading files to CLAM or when starting the
        CLAM server, raises a ParameterException if one or more parameters are not satisfied
        """
        try:
            return self.start(profile, parameter_values=parameter_values)
        except Exception as e:
            self.cleanup()
            raise e

    def start(self, profile, parameter_values=None):
        """
        Add inputs to clam server and starts it.

        :param profile: the profile to run the process with
        :param parameter_values: a dictionary of (key, value) pairs with the parameter values to fill in, only
        overwrites variable parameters
        :return: the status of this project, or a ValueError when an error is encountered with the uploaded files and
        selected profile, an Exception for CLAM errors, or a ParameterException when a parameter is not satisfied
        """
        if parameter_values is None:
            parameter_values = dict()

        if self.status == STATUS_CREATED:
            self.set_status(STATUS_UPLOADING)
            self.set_clam_id(Process.get_random_clam_id())
            clamclient = self.script.get_clam_server()
            clamclient.create(self.clam_id)
            templates = InputTemplate.objects.filter(
                corresponding_profile=profile
            )

            merged_parameters = self.script.get_parameters_as_dict(
                preset_parameters=parameter_values
            )

            if (
                len(
                    self.script.get_unsatisfied_parameters(
                        merged_parameters.keys()
                    )
                )
                != 0
            ):
                raise BaseParameter.ParameterException(
                    "Not all parameters are satisfied"
                )

            self.upload_input_templates(templates)

            clamclient.startsafe(self.clam_id, **merged_parameters)
            self.set_status(STATUS_RUNNING)
            update_script(self.pk)
            return True
        else:
            return False

    def upload_input_templates(self, templates):
        """
        Upload files corresponding to the input templates.

        :param templates: a list of InputTemplate objects
        :return: None, raises a ValueError if there is no file for the template or more than one file for a unique
        template
        """
        clamclient = self.script.get_clam_server()
        for template in templates:
            files = template.is_valid_for(self.folder)
            if not files and not template.optional:
                raise ValueError(
                    "No file specified for template {}".format(template)
                )
            if files:
                if len(files) > 1 and template.unique:
                    raise ValueError(
                        "More than one file specified for unique template {}".format(
                            template
                        )
                    )
                for file in files:
                    full_file_path = os.path.join(self.folder, file)
                    clamclient.addinputfile(
                        self.clam_id, template.template_id, full_file_path
                    )

    def cleanup(self, status=STATUS_CREATED):
        """
        Reset a project on the CLAM server by deleting it and resetting the clam id and status on Django.

        :param status: the status to set the process to after this function has been ran, default=STATUS_CREATED
        :return: None
        """
        if self.clam_id is not None:
            try:
                clamclient = self.script.get_clam_server()
                clamclient.delete(self.clam_id)
            except Exception as e:
                logging.error(e)
        self.clam_id = None
        self.status = status
        self.save()

    def clam_update(self):
        """
        Update a process.

        :return: True when the status was successfully updated (this means the status of this process could also be left
        unchanged), False otherwise
        """
        if self.status == STATUS_RUNNING:
            try:
                clamclient = self.script.get_clam_server()
                data = clamclient.get(self.clam_id)
            except Exception as e:
                logging.error(e)
                return False
            self.update_log_messages_from_xml(data.xml)
            if data.status == clam.common.status.DONE:
                self.set_status(STATUS_WAITING)
            return True
        else:
            return False

    def download_and_delete(self, next_script=None):
        """
        Download all files from a process, decompress them and delete the project from CLAM.

        :return: True if downloading the files and extracting them succeeded, False otherwise
        """
        if (
            self.status == STATUS_WAITING
            or self.status == STATUS_ERROR_DOWNLOAD
        ):
            self.set_status(STATUS_DOWNLOADING)
            if self.download_archive_and_decompress():
                if next_script is not None:
                    self.move_downloaded_output_files(next_script)
                self.cleanup(status=STATUS_FINISHED)
                return True
            else:
                self.set_status(STATUS_ERROR_DOWNLOAD)
                return False
        else:
            return False

    def move_downloaded_output_files(self, script):
        """
        Move downloaded output files that are needed for the next script to the main directory.

        :param script: the next script
        :return: None
        """
        templates = InputTemplate.objects.filter(
            corresponding_profile__script=script
        )
        for template in templates:
            template.move_corresponding_files(self.output_folder, self.folder)

    def download_archive_and_decompress(self):
        """
        Download the output archive from the CLAM server.

        :return: the location of the downloaded archive on success, False on failure
        """
        try:
            clamclient = self.script.get_clam_server()
            if not os.path.exists(self.output_folder):
                os.makedirs(self.output_folder)
            downloaded_archive = os.path.join(
                self.output_folder, self.clam_id + ".{}".format("zip")
            )
            clamclient.downloadarchive(self.clam_id, downloaded_archive, "zip")
            with zipfile.ZipFile(downloaded_archive, "r") as zip_ref:
                zip_ref.extractall(
                    os.path.join(self.folder, self.OUTPUT_FOLDER_NAME)
                )
            os.remove(downloaded_archive)
            return True
        except Exception as e:
            print(
                "An error occurred while downloading and decompressing files from CLAM. Error: {}".format(
                    e
                )
            )
            return False

    def is_finished(self):
        """
        Check if this process is finished.

        :return: True if this process has a status of STATUS_FINISHED, False otherwise
        """
        return self.status == STATUS_FINISHED

    def get_status_messages(self):
        """
        Get the status messages of this process.

        :return: the status messages in a QuerySet
        """
        return LogMessage.objects.filter(process=self)

    def get_status_string(self):
        """
        Get the status of this project in string format.

        :return: a string format of self.status
        """
        if self.status == STATUS_CREATED:
            return "Ready to start"
        elif self.status == STATUS_RUNNING:
            return "Running"
        elif self.status == STATUS_WAITING:
            return "CLAM Done, waiting for download"
        elif self.status == STATUS_DOWNLOADING:
            return "Downloading files from CLAM"
        elif self.status == STATUS_FINISHED:
            return "Done"
        elif self.status == STATUS_ERROR:
            return "An error occurred"
        else:
            return "Unknown"

    def get_status(self):
        """
        Get the status of this project.

        :return: the status of the project
        """
        return self.status

    def get_valid_profiles(self):
        """
        Get the profiles for which the current files meet the requirements.

        :return:
        """
        profiles = Profile.objects.filter(script=self.script)
        valid_profiles = []

        for p in profiles:
            if p.is_valid(self.folder):
                valid_profiles.append(p)
        return valid_profiles

    class Meta:
        """
        Display configuration for admin pane.

        Order admin list alphabetically by name.
        Display plural correctly.
        """

        verbose_name_plural = "Processes"


class LogMessage(Model):
    """Class for saving CLAM log messages."""

    time = DateTimeField(null=True)
    message = CharField(max_length=16384)
    process = ForeignKey(Process, on_delete=CASCADE)
    index = PositiveIntegerField()


class Profile(Model):
    """
    Database model for profiles.

    A profile is a set of InputTemplates (possibly more later on)
    Attributes:
        process                 The process associated with this profile.
    """

    script = ForeignKey(Script, on_delete=SET_NULL, null=True)

    class Meta:
        """
        Display configuration for admin pane.

        Order admin list by id.
        Display plural correctly.
        """

        ordering = ["id"]
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"

    def __str__(self):
        """
        Use identifier in admin pane.

        :return: string including the identifier of this object
        """
        return "Profile {}".format(self.pk)

    def remove_corresponding_templates(self):
        """
        Remove the templates corresponding to this profile object.

        :return: None
        """
        input_templates = InputTemplate.objects.filter(
            corresponding_profile=self
        )
        for template in input_templates:
            template.delete()

    def is_valid(self, folder):
        """
        Check if a profile is valid for a given folder (check if all input templates are valid for a given folder).

        :param folder: the folder to check
        :return: True if all InputTemplates corresponding to this profile are valid for the folder, False otherwise
        """
        templates = InputTemplate.objects.filter(corresponding_profile=self)
        for template in templates:
            if not template.is_valid(folder):
                return False
        return True

    def get_valid_files(self, folder):
        """
        Get a dictionary of valid files for all input templates corresponding to this profile.

        :param folder: the folder to search for the files
        :return: a dictionary of the form:
        dict(
            template.id -> [relative_path_to_valid_file, relative_path_to_valid_file, ...],
            template.id -> [...],
            ...
        )
        containing for each template corresponding to this profile, a set of files corresponding to that template
        """
        templates = InputTemplate.objects.filter(corresponding_profile=self)
        valid_for = dict()
        for template in templates:
            valid_files = template.is_valid_for(folder)
            if valid_files:
                valid_for[template.id] = valid_files
            else:
                valid_for[template.id] = []
        return valid_for

    class IncorrectProfileException(Exception):
        """Exception to be thrown when the project has an incorrect state."""

        pass


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

    template_id = CharField(max_length=1024)
    format = CharField(max_length=1024)
    label = CharField(max_length=1024)
    mime = CharField(max_length=1024, default="text/plain")
    extension = CharField(max_length=32)
    optional = BooleanField()
    unique = BooleanField()
    accept_archive = BooleanField()
    corresponding_profile = ForeignKey(Profile, on_delete=SET_NULL, null=True)

    def move_corresponding_files(self, from_directory, to_directory):
        """
        Move the corresponding files of this template from a directory to a directory (overwrite if necessary).

        :param from_directory: the directory to check files from
        :param to_directory: the directory to move files to
        :return: None
        """
        for file in [
            f
            for f in os.listdir(from_directory)
            if f.endswith("." + self.extension)
        ]:
            shutil.copyfile(
                os.path.join(from_directory, file),
                os.path.join(to_directory, file),
            )

    def is_valid(self, folder):
        """
        Check if a file with the extension of this object is present in the folder.

        :param folder: the folder to search for the file
        :return: True if at least one file is found with the extension from this object, False otherwise
        """
        matching_files = 0
        for file in os.listdir(folder):
            if file.endswith(self.extension):
                matching_files += 1
        if matching_files == 0 and not self.optional:
            return False
        elif matching_files > 1 and self.unique:
            return False
        else:
            return True

    def is_valid_for(self, folder):
        """
        Get all the files corresponding to this input template from a folder.

        :param folder: the folder to search for the files with specific extension
        :return: a list relative paths to with the extension of this object in the folder,
        if no files are found False is returned
        """
        valid_files = list()
        for file in os.listdir(folder):
            if file.endswith(self.extension):
                valid_files.append(file)

        if len(valid_files) == 0:
            return False
        else:
            return valid_files

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
            return "{}{} file with extension {}".format(
                unique, optional, self.extension
            )
        else:
            return "File with extension {}".format(self.extension)

    class Meta:
        """
        Display configuration for admin pane.

        Order admin list by id.
        Display plural correctly.
        """

        ordering = ["id"]
        verbose_name = "Input template"
        verbose_name_plural = "Input templates"


class Pipeline(Model):
    """Pipeline model class."""

    name = CharField(max_length=512)
    fa_script = ForeignKey(
        Script,
        on_delete=CASCADE,
        blank=False,
        null=False,
        related_name="fa_script",
    )
    g2p_script = ForeignKey(
        Script,
        on_delete=CASCADE,
        blank=False,
        null=False,
        related_name="g2p_script",
    )

    def __str__(self):
        """
        Convert this object to a string.

        :return: the name property of this object
        """
        return self.name


class Project(Model):
    """Project model class."""

    UPLOADING = 0
    FA_RUNNING = 1
    G2P_RUNNING = 2
    CHECK_DICTIONARY = 3

    TYPES = (
        (UPLOADING, "Uploading"),
        (FA_RUNNING, "FA running"),
        (G2P_RUNNING, "G2P running"),
        (CHECK_DICTIONARY, "Check dictionary"),
    )

    name = CharField(max_length=512)
    folder = FilePathField(
        allow_folders=True, allow_files=False, path=user_data_folder_path
    )
    pipeline = ForeignKey(Pipeline, on_delete=CASCADE, blank=False, null=False)
    user = ForeignKey(User, on_delete=SET_NULL, null=True)
    current_process = ForeignKey(
        Process, on_delete=SET_NULL, null=True, blank=True
    )

    def __str__(self):
        """Convert this object to string."""
        return self.name

    @staticmethod
    def create_project(name, pipeline, user):
        """
        Create a project, also create a directory for storing the files of the created project.

        :param name: the name of the project, per user there can only be one unique project per name
        :param pipeline: the pipeline for which to create the project
        :param user: the user for which to create the project
        :return: a ValueError if either the project name or directory already exists, otherwise a new Project object
        """
        project_qs = Project.objects.filter(name=name, user=user)
        if project_qs.exists():
            raise ValueError(
                "Failed to create project, project called {} from {} does already exist.".format(
                    name, user
                )
            )
        else:
            folder = os.path.join(
                os.path.join(settings.USER_DATA_FOLDER, user.username), name
            )
            if os.path.exists(folder):
                raise ValueError(
                    "Failed to create project, folder {} does already exist.".format(
                        folder
                    )
                )
            else:
                os.makedirs(folder)
                return Project.objects.create(
                    name=name, folder=folder, pipeline=pipeline, user=user
                )

    @property
    def status(self):
        """
        GET the status of this project.

        :return: the next step of this project
        """
        return self.get_next_step()

    def get_next_step(self):
        """
        Get the project status.

        :return: a value in self.TYPES indicating the project status
        """
        if self.current_process is None:
            if self.finished_fa():
                return self.CHECK_DICTIONARY
            else:
                return self.UPLOADING
        else:
            if self.current_process.script == self.pipeline.fa_script:
                return self.FA_RUNNING
            elif self.current_process.script == self.pipeline.g2p_script:
                return self.G2P_RUNNING
            else:
                raise ValueError(
                    "Current script process is not an FA or G2P script"
                )

    def write_oov_dict_file_contents(self, content, name="default.oov.dict"):
        """
        Write content to .oov.dict file in project folder.

        :param content: the content to write to the file
        :param name: the name of the default file to write to
        :return: None
        """
        path = self.get_oov_dict_file_path()
        if path is not None:
            with open(path, "w") as file:
                file.write(content)
        else:
            with open(os.path.join(self.folder, name), "w") as file:
                file.write(content)

    def get_oov_dict_file_contents(self):
        """
        Get the content of the .oov.dict file in the project folder.

        :return: the content of the .oov.dict file, an emtpy string if such a file does not exist
        """
        path = self.get_oov_dict_file_path()
        if path is not None:
            with open(path, "r") as file:
                return file.read()
        else:
            return ""

    def get_oov_dict_file_path(self):
        """
        Get the file path of the .oov.dict file in the folder directory.

        :return: the file path of the .oov.dict file, or None if such a file does not exist
        """
        for file_name in os.listdir(self.folder):
            full_file_path = os.path.join(self.folder, file_name)
            if os.path.isfile(full_file_path):
                if file_name.endswith(".oov.dict"):
                    return full_file_path
        return None

    def has_non_empty_extension_file(self, extensions):
        """
        Check if a file ends with some extension.

        :param extensions: a list of extensions that are valid.
        :return: True if an .extension file is present with some text, False otherwise. Note: we may have multiple
        files, but as long as one is non empty we return true. (e.g. we have a.ext and b.ext, a is empty but b is not
        thus we return true).
        """
        if type(extensions) is not list:
            raise TypeError("Extensions must be a list type")
        for file_name in os.listdir(self.folder):
            full_file_path = os.path.join(self.folder, file_name)
            if os.path.isfile(full_file_path):
                if file_name.endswith(tuple(extensions)):
                    if os.stat(full_file_path).st_size != 0:
                        return True

        return False

    def finished_fa(self):
        """
        Check if FA has finished.

        :return: True if a .ctm file is present in the project directory, False otherwise
        """
        return self.has_non_empty_extension_file(["ctm"])

    def create_downloadable_archive(self):
        """
        Create a downloadable archive.

        :return: the filename of the downloadable archive
        """
        _, zip_filename = os.path.split(self.folder)
        zip_filename = zip_filename + ".zip"
        return os.path.join(
            self.folder,
            zip_dir(self.folder, os.path.join(self.folder, zip_filename)),
        )

    def can_upload(self):
        """
        Check whether files can be uploaded to this project.

        :return: True if files can be uploaded to this project, False otherwise
        """
        return self.current_process is None

    def can_start_new_process(self):
        """
        Check whether a new process can be started for this project.

        :return: True if there are not running processes for this project, False otherwise
        """
        return self.current_process is None

    def start_fa_script(self, profile, **kwargs):
        """
        Start the FA script with a given profile.

        :param profile: the profile to start FA with
        :return: the process with the started script, raises a ValueError if the files in the folder do not match the
        profile, raises an Exception if a CLAM error occurred
        """
        return self.start_script(profile, self.pipeline.fa_script, **kwargs)

    def start_g2p_script(self, profile, **kwargs):
        """
        Start the G2P script with a given profile.

        :param profile: the profile to start G2P with
        :return: the process with the started script, raises a ValueError if the files in the folder do not match the
        profile, raises an Exception if a CLAM error occurred
        """
        return self.start_script(profile, self.pipeline.g2p_script, **kwargs)

    def start_script(self, profile, script, parameter_values=None):
        """
        Start a new script and add the process to this project.

        :param parameter_values: parameter values in (key, value) format in a dictionary
        :param profile: the profile to start the script with
        :param script: the script to start
        :return: the process with the started script, raises a ValueError if the files in the folder do not match the
        profile, raises an Exception if a CLAM error occurred
        """
        parameter_values = (
            dict() if parameter_values is None else parameter_values
        )

        if not self.can_start_new_process():
            raise Project.StateException
        elif profile.script != script:
            raise Profile.IncorrectProfileException

        self.current_process = Process.objects.create(
            script=script, folder=self.folder
        )
        self.save()
        try:
            self.current_process.start_safe(
                profile, parameter_values=parameter_values
            )
            return self.current_process
        except Exception as e:
            self.cleanup()
            raise e

    def cleanup(self):
        """
        Reset the project to a clean state.

        Resets the current process to None
        :return: None
        """
        self.current_process = None
        self.save()

    def delete(self, **kwargs):
        """
        Delete a Project.

        :param kwargs: keyword arguments
        :return: None, deletes a project and removes the folder of that project
        """
        if os.path.exists(self.folder):
            shutil.rmtree(self.folder, ignore_errors=True)
        super(Project, self).delete(**kwargs)

    def is_project_script(self, script):
        """
        Check if a script corresponds to this project.

        :param script: the script to check
        :return: True if it corresponds to this project, False otherwise
        """
        return (
            script == self.pipeline.fa_script
            or script == self.pipeline.g2p_script
        )

    class StateException(Exception):
        """Exception to be thrown when the project has an incorrect state."""

        pass

    class Meta:
        """Meta class for Project model."""

        unique_together = ("name", "user")
        permissions = [
            ("access_project", "Access project"),
        ]


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

    name = CharField(max_length=1024)
    corresponding_script = ForeignKey(Script, on_delete=SET_NULL, null=True)
    preset = BooleanField(default=False)
    type = IntegerField(choices=TYPES)

    @staticmethod
    def get_type(parameter):
        """
        Get the type of a CLAM parameter.

        :param parameter: the CLAM parameter object
        :return: the type of the CLAM parameter in BaseParameter.TYPES types
        """
        if parameter.__class__ == clam.common.parameters.BooleanParameter:
            return BaseParameter.BOOLEAN_TYPE
        elif parameter.__class__ == clam.common.parameters.StaticParameter:
            return BaseParameter.STATIC_TYPE
        elif parameter.__class__ == clam.common.parameters.StringParameter:
            return BaseParameter.STRING_TYPE
        elif parameter.__class__ == clam.common.parameters.ChoiceParameter:
            return BaseParameter.CHOICE_TYPE
        elif parameter.__class__ == clam.common.parameters.TextParameter:
            return BaseParameter.TEXT_TYPE
        elif parameter.__class__ == clam.common.parameters.IntegerParameter:
            return BaseParameter.INTEGER_TYPE
        elif parameter.__class__ == clam.common.parameters.FloatParameter:
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

    def remove_corresponding_presets(self):
        """
        Remove all typed parameters corresponding to this parameter.

        :return: None
        """
        parameter_classes = [
            BooleanParameter,
            StaticParameter,
            StringParameter,
            ChoiceParameter,
            TextParameter,
            IntegerParameter,
            FloatParameter,
        ]
        for parameter_class in parameter_classes:
            try:
                obj = parameter_class.objects.get(base=self)
                if parameter_class.__class__ == ChoiceParameter:
                    obj.remove_corresponding_choices()
                obj.delete()
            except parameter_class.DoesNotExist:
                pass

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


class BooleanParameter(Model):
    """Parameter for boolean values."""

    base = OneToOneField(BaseParameter, on_delete=SET_NULL, null=True)
    value = BooleanField(default=False, null=True, blank=True)

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

    base = OneToOneField(BaseParameter, on_delete=SET_NULL, null=True)
    value = CharField(max_length=2048, null=True, blank=True)

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

    base = OneToOneField(BaseParameter, on_delete=SET_NULL, null=True)
    value = CharField(max_length=2048, null=True, blank=True)

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
        "ChoiceParameter", on_delete=SET_NULL, null=True
    )
    value = CharField(max_length=2048)

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

    base = OneToOneField(BaseParameter, on_delete=SET_NULL, null=True)
    value = ForeignKey(Choice, on_delete=SET_NULL, null=True, blank=True)

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

    base = OneToOneField(BaseParameter, on_delete=SET_NULL, null=True)
    value = TextField(null=True, blank=True)

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

    base = OneToOneField(BaseParameter, on_delete=SET_NULL, null=True)
    value = IntegerField(null=True, blank=True)

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

    base = OneToOneField(BaseParameter, on_delete=SET_NULL, null=True)
    value = FloatField(null=True, blank=True)

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
