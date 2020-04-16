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
from django.contrib.auth import get_user_model
import zipfile
from .services import zip_dir

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

User = get_user_model()


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

    script = ForeignKey(Script, on_delete=SET_NULL, blank=False, null=True)
    clam_id = CharField(max_length=256, null=True)
    status = IntegerField(choices=STATUS, default=0)
    folder = FilePathField(
        allow_folders=True, allow_files=False, path=settings.USER_DATA_FOLDER
    )

    @staticmethod
    def get_random_clam_id():
        """
        Get a random 32 bit string.

        :return: a random 32 bit string
        """
        return secrets.token_hex(32)

    @staticmethod
    def create_process(script, folder):
        """
        Start a project.

        :param script: the script
        :param folder: the upload/download folder for the clam server, the folder must contain at least all the required
        files in one of the linked input templates before starting this process
        :return: the process
        """
        random_token = Process.get_random_clam_id()
        try:
            clamclient = script.get_clam_server()
            clamclient.create(random_token)
            data = clamclient.get(random_token)
            clamclient.delete(random_token)
        except Exception as e:
            logging.error(e)
            return False
        process = Process.objects.create(
            script=Script.objects.get(pk=script.id),
            clam_id=None,
            folder=folder,
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

    def start_safe(self, profile):
        """
        Start uploading files to CLAM and start the CLAM server in a safe way.

        Actually only executes the start() method and runs the cleanup() method when an exception is raised.
        :param profile: the profile to start this process with
        :return: True when the process was started, False otherwise, raises a ValueError if there was an error with the
        input templates, raises an Exception if there was an error when uploading files to CLAM or when starting the
        CLAM server
        """
        try:
            return self.start(profile)
        except ValueError as e:
            # Input template error
            self.cleanup()
            raise e
        except Exception as e:
            # CLAM error
            self.cleanup()
            raise e

    def start(self, profile):
        """
        Add inputs to clam server and starts it.

        :param profile: the profile to run the process with
        :return: the status of this project, or a ValueError when an error is encountered with the uploaded files and
        selected profile, or an Exception for CLAM errors
        """
        if self.status == STATUS_CREATED:
            self.set_status(STATUS_UPLOADING)
            self.set_clam_id(Process.get_random_clam_id())
            clamclient = self.script.get_clam_server()
            clamclient.create(self.clam_id)
            templates = InputTemplate.objects.filter(
                corresponding_profile=profile
            )

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
            clamclient.startsafe(self.clam_id)
            self.set_status(STATUS_RUNNING)
            return True
        else:
            return False

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

    def download_and_delete(self):
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
                self.cleanup(status=STATUS_FINISHED)
                return True
            else:
                self.set_status(STATUS_ERROR_DOWNLOAD)
                return False
        else:
            return False

    def download_archive_and_decompress(self):
        """
        Download the output archive from the CLAM server.

        :return: the location of the downloaded archive on success, False on failure
        """
        try:
            clamclient = self.script.get_clam_server()
            downloaded_archive = self.get_output_file_name()
            clamclient.downloadarchive(self.clam_id, downloaded_archive, "zip")
            with zipfile.ZipFile(downloaded_archive, "r") as zip_ref:
                zip_ref.extractall(self.folder)
            os.remove(downloaded_archive)
            return True
        except Exception as e:
            print(
                "An error occurred while downloading and decompressing files from CLAM. Error: {}".format(
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

    def get_output_file_name(self, extension=".zip"):
        """
        Get a name of an not existing file to store data to.

        :return: a path to a non existing file
        """
        return os.path.join(self.folder, self.clam_id + ".{}".format(extension))

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

    def remove_corresponding_profiles(self):
        """
        Remove all profiles corresponding to this process.

        :return: None
        """
        profiles = Profile.objects.filter(process=self)
        for profile in profiles:
            profile.remove_corresponding_templates()
            profile.delete()

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

    def is_valid(self, folder):
        """
        Check if a file with the extension of this object is present in the folder.

        :param folder: the folder to search for the file
        :return: True if at least one file is found with the extension from this object, False otherwise
        """
        for file in os.listdir(folder):
            if file.endswith(self.extension):
                return True
        return False

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

    name = CharField(max_length=512)
    folder = FilePathField(
        allow_folders=True, allow_files=False, path=settings.USER_DATA_FOLDER
    )
    pipeline = ForeignKey(Pipeline, on_delete=CASCADE, blank=False, null=False)
    user = ForeignKey(User, on_delete=SET_NULL, null=True)
    current_process = ForeignKey(
        Process, on_delete=SET_NULL, null=True, blank=True
    )

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

    def write_oov_dict_file_contents(self, content):
        """
        Write content to .oov.dict file in project folder.

        :param content: the content to write to the file
        :return: None
        """
        path = self.get_oov_dict_file_path()
        if path is not None:
            with open(path, "w") as file:
                file.write(content)
        else:
            # TODO: Change the way we handle writing to a .oov.dict that does not exist
            with open(
                os.path.join(self.folder, "default.oov.dict"), "w"
            ) as file:
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
        for file_name in os.listdir(self.folder):
            full_file_path = os.path.join(self.folder, file_name)
            if os.path.isfile(full_file_path):
                if file_name.endswith(
                    tuple(extensions)
                ):  # a python tuple can be of any size btw.
                    if os.stat(full_file_path).st_size != 0:
                        return True

        return False

    def finished_fa(self):
        """
        Check if FA has finished.

        :return: True if a .ctm file is present in the project directory, False otherwise
        """
        return self.has_non_empty_extension_file('ctm')

    def create_downloadable_archive(self):
        """
        Create a downloadable archive.

        :return: the filename of the downloadable archive
        """
        _, zip_filename = os.path.split(self.folder)
        zip_filename = zip_filename + '.zip'
        return os.path.join(self.folder, zip_dir(self.folder, os.path.join(self.folder, zip_filename)))

    class StateException(Exception):
        """Exception to be throwed when the project has an incorrect state."""

        pass

    class Meta:
        """Meta class for Project model."""

        unique_together = ("name", "user")
