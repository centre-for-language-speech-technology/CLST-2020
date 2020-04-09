import pytz
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

# Create your models here.

STATUS_CREATED = 0
STATUS_RUNNING = 1
STATUS_DOWNLOAD = 2
STATUS_DOWNLOADING = 3
STATUS_FINISHED = 4
STATUS_ERROR = -1


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

    img = ImageField(
        upload_to="script_img",
        blank=True,
        help_text="Thumbnail to symbolize script",
    )
    # If no image is provided, the icon is used instead

    description = TextField(max_length=32768, blank=True)

    forced_alignment_script = BooleanField(default=True)

    username = CharField(max_length=200, blank=True)
    password = CharField(max_length=200, blank=True)

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


class Process(Model):
    """
    Database model for processes in CLAM.

    Attributes:
        name                          Name of the process.
                                      Used for identification only, can be anything.
        clam_id                       Identification number given by CLAM.
        output_path                   Path to the primary output file (e.g. output/error.log)
    """

    name = CharField(max_length=512, blank=False)
    script = ForeignKey(Script, on_delete=SET_NULL, blank=False, null=True)
    clam_id = CharField(max_length=256, blank=True)
    output_path = CharField(max_length=512, default="output/error.log")
    status = IntegerField(default=STATUS_CREATED)
    # TODO: Change this to a field of our user's files
    output_file = CharField(max_length=512, default=None, null=True, blank=True)

    @staticmethod
    def create_project(project_name, script):
        """
        Start a project.

        :param project_name: the project name
        :param script: the script
        :return: the process
        """
        random_token = secrets.token_hex(32)
        clamclient = script.get_clam_server()
        clamclient.create(random_token)
        data = clamclient.get(random_token)
        process = Process.objects.create(
            name=project_name,
            script=Script.objects.get(pk=script.id),
            clam_id=random_token,
        )
        Profile.create_templates_from_data(process, data.inputtemplates())
        return process

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
                tz = pytz.timezone(settings.TIME_ZONE)
                time = tz.localize(
                    datetime.datetime.strptime(
                        item.attrib["time"], "%d/%b/%Y %H:%M:%S"
                    )
                )
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

    def start(self, argument_files):
        """
        Add inputs to clam server and starts it.

        :param argument_files: the argument files to add
        :return: None
        """
        clamclient = self.script.get_clam_server()
        # TODO: Check if files are already on the CLAM server before uploading, otherwise this will throw an error
        for (file, template) in argument_files:
            clamclient.addinputfile(self.clam_id, template, file)

        clamclient.startsafe(self.clam_id)
        self.status = STATUS_RUNNING
        self.save()

    def clam_update(self):
        """
        Update a process.

        :return: this process' status
        """
        if self.status == STATUS_RUNNING:
            clamclient = self.script.get_clam_server()
            data = clamclient.get(self.clam_id)
            self.update_log_messages_from_xml(data.xml)
            if data.status == clam.common.status.DONE:
                self.status = STATUS_DOWNLOAD
                self.save()
        elif self.status == STATUS_DOWNLOAD:
            self.status = STATUS_DOWNLOADING
            self.save()
            archive = self.download_archive_and_delete()
            if archive:
                self.status = STATUS_FINISHED
                self.output_file = archive
                self.save()
        return self.status

    def download_archive(self, extension="zip"):
        """
        Download the output archive from the CLAM server.

        :param extension: the extension to use for downloading
        :return: the location of the downloaded archive on success, False on failure
        """
        try:
            clamclient = self.script.get_clam_server()
            downloaded_archive = self.get_output_file_name(extension)
            clamclient.downloadarchive(
                self.clam_id, downloaded_archive, extension
            )
            return downloaded_archive
        except Exception as e:
            logging.error(
                "An exception occurred while downloading files from CLAM. Exception: {}".format(
                    e
                )
            )
            return False

    def download_archive_and_delete(self, extension="zip"):
        """
        Download the output archive from the CLAM server and then delete the project on the CLAM server.

        :param extension: the extension to use for downloading
        :return: the location of the downloaded archive on success, False on failure
        """
        try:
            clamclient = self.script.get_clam_server()
            downloaded_archive = self.get_output_file_name(extension)
            clamclient.downloadarchive(
                self.clam_id, downloaded_archive, extension
            )
            clamclient.delete(self.clam_id)
            return downloaded_archive
        except Exception as e:
            logging.error(
                "An exception occurred while downloading files from CLAM. Exception: {}".format(
                    e
                )
            )
            return False

    def get_status_messages(self):
        """
        Get the status messages of this process.

        :return: the status messages in a QuerySet
        """
        return LogMessage.objects.filter(process=self)

    def get_output_file_name(self, extension):
        """
        Get a name of an not existing file to store data to.

        :return: a path to a non existing file
        """
        # TODO: Implement this method
        return os.path.join(
            settings.DOWNLOAD_DIR, self.clam_id + ".{}".format(extension)
        )

    def __str__(self):
        """Use name of process in admin display."""
        return self.name

    def get_status_string(self):
        """
        Get the status of this project in string format.

        :return: a string format of self.status
        """
        if self.status == STATUS_CREATED:
            return "Ready to start"
        elif self.status == STATUS_RUNNING:
            return "Running"
        elif self.status == STATUS_DOWNLOAD:
            return "Downloading results from CLAM server"
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

    class Meta:
        """
        Display configuration for admin pane.

        Order admin list alphabetically by name.
        Display plural correctly.
        """

        ordering = ["name"]
        verbose_name_plural = "Processes"


class LogMessage(Model):
    """Class for saving CLAM log messages."""

    time = DateTimeField()
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

    process = ForeignKey(Process, on_delete=SET_NULL, null=True)

    class Meta:
        """
        Display configuration for admin pane.

        Order admin list by id.
        Display plural correctly.
        """

        ordering = ["id"]
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"

    @staticmethod
    def create_templates_from_data(process, inputtemplates):
        """Create template objects from data."""
        new_profile = Profile.objects.create(process=process)
        for input_template in inputtemplates:
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
        """
        Use identifier in admin pane.

        :return: string including the identifier of this object
        """
        return str(self.id)


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

    class Meta:
        """
        Display configuration for admin pane.

        Order admin list by id.
        Display plural correctly.
        """

        ordering = ["id"]
        verbose_name = "Input template"
        verbose_name_plural = "Input templates"


class InputFile(Model):
    """
    Database model for files used as inputs of scripts.

    Attributes:
        name                          Name of the file. 
                                      Used for identification only, can be anything.
        input_file                    Input file on disk.
        description                   Documentation of the purpose/content of the file.
        associated_process            Process object the file belongs to.
    """

    name = CharField(max_length=512)
    input_file = FilePathField(path="uploads/")  # TODO change this
    description = TextField(max_length=32768)
    associated_process = ManyToManyField(Process, default=None)

    def __str__(self):
        """Use name of input file in admin display."""
        return self.name
