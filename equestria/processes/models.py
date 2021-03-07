import datetime
import logging
import os
import re
import secrets
import shutil
import xml.etree.ElementTree as ET
import zipfile

import pytz
from clam.common import status
from django.conf import settings
from django.db import models
from processes.tasks import update_script
from projects.models import File, Project
from scripts.models import (
    Script,
    InputTemplate,
    BaseParameter,
    Profile,
    OutputTemplate,
)


class Process(models.Model):
    """
    Database model for processes in CLAM.

    Attributes:
        name                          Name of the process.
                                      Used for identification only, can be anything.
        clam_id                       Identification number given by CLAM.
        output_path                   Path to the primary output file (e.g. output/error.log)
    """

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

    script = models.ForeignKey(
        Script,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        help_text="The Script for which this Process is " "being ran.",
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        help_text="The Project for which this Process is" "being ran.",
    )
    clam_id = models.CharField(
        max_length=256,
        null=True,
        default=None,
        help_text="The CLAM Project name that is being "
        "used on the CLAM server to run this "
        "Process.",
    )
    status = models.IntegerField(
        choices=STATUS,
        default=0,
        help_text="The current status of this Process. This will "
        "be automatically mirrored with the CLAM server.",
    )
    folder = models.FilePathField(
        allow_folders=True,
        allow_files=False,
        path="media/processes",
        help_text="The folder to write all output files " "of this Process to.",
    )
    created = models.DateTimeField(
        auto_now_add=True,
        null=False,
        blank=False,
        help_text="The time that this Process " "was created.",
    )

    def __str__(self):
        """Convert this object to string."""
        return "Process for {} ({})".format(
            self.script, Process.STATUS[self.status][1]
        )

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

        if self.status == Process.STATUS_CREATED:
            self.set_status(Process.STATUS_UPLOADING)
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
            self.set_status(Process.STATUS_RUNNING)
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
            file_settings = FileSetting.objects.filter(
                input_template=template, file__project=self.project
            )
            for file_setting in file_settings:
                clamclient.addinputfile(
                    self.clam_id,
                    template.template_id,
                    file_setting.file.absolute_file_path,
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
        if self.status == Process.STATUS_RUNNING:
            try:
                clamclient = self.script.get_clam_server()
                data = clamclient.get(self.clam_id)
            except Exception as e:
                logging.error(e)
                return False
            self.update_log_messages_from_xml(data.xml)
            if data.status == status.DONE:
                self.set_status(Process.STATUS_WAITING)
            return True
        else:
            return False

    def download_and_cleanup(self):
        """
        Download all files from a process, decompress them and delete the project from CLAM.

        :return: True if downloading the files and extracting them succeeded, False otherwise
        """
        if (
            self.status == Process.STATUS_WAITING
            or self.status == Process.STATUS_ERROR_DOWNLOAD
        ):
            self.set_status(Process.STATUS_DOWNLOADING)
            if self.download_archive_and_decompress():
                self.move_downloaded_output_files()
                self.cleanup(status=Process.STATUS_FINISHED)
                return True
            else:
                self.set_status(Process.STATUS_ERROR_DOWNLOAD)
                return False
        else:
            return False

    def move_downloaded_output_files(self, files=None):
        """
        Move downloaded output files that are needed for the next script to the main directory.

        :return: None
        """
        for file in self.file_list:
            if (
                files is None
                and OutputTemplate.match_any(file, self.script.output_templates)
            ) or (files is not None and file in files):
                file_obj, created = File.objects.get_or_create(
                    file=os.path.join(self.project.folder, file),
                    project=self.project,
                )
                file_obj.save()
                shutil.copy(
                    os.path.join(self.absolute_process_folder, file),
                    os.path.join(
                        self.project.absolute_path, file_obj.absolute_file_path
                    ),
                )

    def download_archive_and_decompress(self):
        """
        Download the output archive from the CLAM server.

        :return: the location of the downloaded archive on success, False on failure
        """
        try:
            clamclient = self.script.get_clam_server()
            os.makedirs(self.absolute_process_folder, exist_ok=True)
            clamclient.downloadarchive(
                self.clam_id, self.absolute_output_archive_path, "zip"
            )
            with zipfile.ZipFile(
                self.absolute_output_archive_path, "r"
            ) as zip_ref:
                zip_ref.extractall(self.absolute_process_folder)
            os.remove(self.absolute_output_archive_path)
            return True
        except Exception as e:
            logging.error(
                "An error occurred while downloading and decompressing files from CLAM. Error: {}".format(
                    e
                )
            )
            return False

    @property
    def finished(self):
        """
        Check if this process is finished.

        :return: True if this process has a status of STATUS_FINISHED, False otherwise
        """
        return self.status == Process.STATUS_FINISHED

    @property
    def log_messages(self):
        """
        Get the status messages of this process.

        :return: the status messages in a QuerySet
        """
        return LogMessage.objects.filter(process=self).order_by("index")

    @property
    def absolute_process_folder(self):
        """Get the absolute process folder path."""
        return os.path.join(
            os.path.join(settings.MEDIA_ROOT, settings.PROCESS_DATA_FOLDER),
            str(self.id),
        )

    @property
    def absolute_output_archive_path(self):
        """Get the absolute path to the output archive."""
        return os.path.join(self.absolute_process_folder, "output-archive.zip")

    def get_status_string(self):
        """
        Get the status of this project in string format.

        :return: a string format of self.status
        """
        if self.status == Process.STATUS_CREATED:
            return "Ready to start"
        elif self.status == Process.STATUS_RUNNING:
            return "Running"
        elif self.status == Process.STATUS_WAITING:
            return "CLAM Done, waiting for download"
        elif self.status == Process.STATUS_DOWNLOADING:
            return "Downloading files from CLAM"
        elif self.status == Process.STATUS_FINISHED:
            return "Done"
        elif self.status == Process.STATUS_ERROR:
            return "An error occurred"
        elif self.status == Process.STATUS_ERROR_DOWNLOAD:
            return "Error while downloading files from CLAM"
        else:
            return "Unknown"

    @property
    def file_list(self):
        """Get a file list of the files in the output directory of the process."""
        return [
            x
            for x in os.listdir(self.absolute_process_folder)
            if os.path.isfile(os.path.join(self.absolute_process_folder, x))
        ]

    class Meta:
        """
        Display configuration for admin pane.

        Order admin list alphabetically by name.
        Display plural correctly.
        """

        verbose_name_plural = "Processes"


class LogMessage(models.Model):
    """Class for saving CLAM log messages."""

    time = models.DateTimeField(
        null=True, help_text="The time of the log message."
    )
    message = models.CharField(max_length=16384, help_text="The log message.")
    process = models.ForeignKey(
        Process,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        help_text="The process for which this log message " "is.",
    )
    index = models.PositiveIntegerField(
        help_text="The index of the log message. Log messages will be sorted on their"
        " index."
    )


class FileSetting(models.Model):
    """Class for adding Files to InputTemplates."""

    file = models.ForeignKey(
        File,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        help_text="The file for which this file setting is " "specified.",
    )
    input_template = models.ForeignKey(
        InputTemplate,
        related_name="file_settings",
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        help_text="The Input Template to register the File Setting for.",
    )

    @staticmethod
    def create_for_file_presets(
        input_template: InputTemplate, project: Project
    ):
        """Create file settings automatically for the input template using the file presets."""
        file_presets = FilePreset.objects.filter(input_template=input_template)
        file_preset_files = [
            x
            for x in project.files
            if FilePreset.match_any(x.filename, file_presets)
        ]
        if len(file_preset_files) == 1 and input_template.unique:
            return [
                FileSetting.objects.get_or_create(
                    file=x, input_template=input_template
                )
                for x in file_preset_files
            ]
        elif not input_template.unique:
            return [
                FileSetting.objects.get_or_create(
                    file=x, input_template=input_template
                )
                for x in file_preset_files
            ]
        else:
            return []

    @staticmethod
    def create_for_input_template(
        input_template: InputTemplate, project: Project
    ):
        """Create file settings automatically for the input template."""
        file_presets = FileSetting.create_for_file_presets(
            input_template, project
        )
        if len(file_presets) > 0:
            return file_presets

        files_with_extension = project.get_files_with_extension(
            input_template.extension
        )
        if input_template.unique and len(files_with_extension) == 1:
            return [
                FileSetting.objects.get_or_create(
                    file=files_with_extension[0], input_template=input_template
                )
            ]
        elif not input_template.unique:
            return [
                FileSetting.objects.get_or_create(
                    file=x, input_template=input_template
                )
                for x in files_with_extension
            ]
        else:
            return []


class ParameterSetting(models.Model):
    """Class for parameter settings."""

    class InvalidValueType(Exception):
        """Exeception indicating that a ParameterSetting has an incorrect type."""

        pass

    _value = models.CharField(
        max_length=1024,
        help_text="The value of the Parameter Setting in string format.",
    )
    base_parameter = models.ForeignKey(
        BaseParameter,
        related_name="parameter_setting",
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        help_text="The Base Parameter to register the Parameter Setting for.",
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        help_text="The Project for which to register the " "Parameter Setting.",
    )

    @property
    def raw_value(self):
        """Get the raw value."""
        return self._value

    @property
    def value(self):
        """Get the value as the intended type."""
        if self.base_parameter.type == BaseParameter.BOOLEAN_TYPE:
            return (
                self._value != "0"
                and self._value != "false"
                and self._value != "False"
            )
        elif self.base_parameter.type == BaseParameter.STATIC_TYPE:
            return self._value
        elif self.base_parameter.type == BaseParameter.STRING_TYPE:
            return self._value
        elif self.base_parameter.type == BaseParameter.CHOICE_TYPE:
            choice_parameter = self.base_parameter.get_typed_parameter()
            if choice_parameter is not None:
                choices = choice_parameter.get_available_choices()
                for choice in choices:
                    if choice.value == self._value:
                        return choice
                raise ValueError(
                    "Choice does not exist for base parameter {} and choice {}.".format(
                        self.base_parameter, self._value
                    )
                )
            raise ValueError(
                "Choice parameter does not exist for base parameter {}".format(
                    self.base_parameter
                )
            )
        elif self.base_parameter.type == BaseParameter.TEXT_TYPE:
            return self._value
        elif self.base_parameter.type == BaseParameter.INTEGER_TYPE:
            return int(self._value)
        elif self.base_parameter.type == BaseParameter.FLOAT_TYPE:
            return float(self._value)
        else:
            raise TypeError(
                "Type of parameter {} unknown".format(self.base_parameter)
            )

    def has_right_value_type(self):
        """Check if the type of the _value field is correct."""
        if self.base_parameter.type == BaseParameter.BOOLEAN_TYPE:
            return True
        elif self.base_parameter.type == BaseParameter.STATIC_TYPE:
            return True
        elif self.base_parameter.type == BaseParameter.STRING_TYPE:
            return True
        elif self.base_parameter.type == BaseParameter.CHOICE_TYPE:
            choice_parameter = self.base_parameter.get_typed_parameter()
            if choice_parameter is not None:
                return self._value in [
                    x.value for x in choice_parameter.get_available_choices()
                ]
        elif self.base_parameter.type == BaseParameter.TEXT_TYPE:
            return True
        elif self.base_parameter.type == BaseParameter.INTEGER_TYPE:
            try:
                int(self._value)
                return True
            except ValueError:
                return False
        elif self.base_parameter.type == BaseParameter.FLOAT_TYPE:
            try:
                float(self._value)
                return True
            except ValueError:
                return False
        return False

    def save(
        self,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        """Save this model."""
        if self.has_right_value_type():
            return super().save(
                force_insert=force_insert,
                force_update=force_update,
                using=using,
                update_fields=update_fields,
            )
        else:
            raise ParameterSetting.InvalidValueType(
                "Type validation for {} failed".format(self)
            )

    class Meta:
        """Meta class."""

        unique_together = ("base_parameter", "project")


class FilePreset(models.Model):
    """File presets."""

    input_template = models.ForeignKey(
        InputTemplate,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        help_text="The Input template for which to "
        "register the File Preset. When "
        "automatic configuration of File "
        "Settings is being ran by a User, "
        "all File Presets of an Input "
        "template will try to match files in"
        " the corresponding Project. If one"
        " matches it will be created as a"
        " File Setting.",
    )
    regex = models.CharField(
        max_length=1024,
        null=False,
        blank=False,
        help_text="The regular expression to use when "
        "matching file names of a Project.",
    )

    def __init__(self, *args, **kwargs):
        """Initialize file preset."""
        super().__init__(*args, **kwargs)
        self._regex = re.compile(self.regex)

    @staticmethod
    def match_any(filename, filepresets):
        """Match any filename against a list of filepresets."""
        for filepreset in filepresets:
            if filepreset.match(filename):
                return True
        return False

    def match(self, filename):
        """Match a filename against this file preset."""
        return self._regex.match(filename)


class PreferableFile(models.Model):
    """File list extension."""

    input_template = models.ForeignKey(
        InputTemplate,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        help_text="The Input template for which to "
        "register the File list regular expression. Files that match the regular expression are shown in the"
        "Process configuration window under this input template.",
    )
    regex = models.CharField(
        max_length=1024,
        null=False,
        blank=False,
        help_text="The regular expression to use when "
        "matching file names of a Project.",
    )

    def __init__(self, *args, **kwargs):
        """Initialize file preset."""
        super().__init__(*args, **kwargs)
        self._regex = re.compile(self.regex)

    @staticmethod
    def match_any(filename, filepresets):
        """Match any filename against a list of filepresets."""
        for filepreset in filepresets:
            if filepreset.match(filename):
                return True
        return False

    def match(self, filename):
        """Match a filename against this file preset."""
        return self._regex.match(filename)
