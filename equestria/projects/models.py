import os
import shutil
import zipfile
from pathlib import Path

from scripts.models import Profile
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from pipelines.models import Pipeline, DictionaryFileFormat
from .services import remove_files_from_directory

User = get_user_model()


def project_folder_path(instance, filename):
    """Get a project folder path."""
    return os.path.join(instance.project.folder, filename)


class Project(models.Model):
    """Project model class."""

    name = models.CharField(
        max_length=512, help_text="The name of the Project."
    )
    pipeline = models.ForeignKey(
        Pipeline,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        help_text="The Pipeline this Project belongs to.",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        help_text="The User this Project belongs to.",
    )

    @property
    def absolute_path(self):
        """Get the absolute path of the project folder."""
        return os.path.join(
            os.path.join(
                os.path.join(settings.MEDIA_ROOT, settings.USER_DATA_FOLDER),
                self.user.username,
            ),
            self.name,
        )

    def get_files_with_extension(self, extension):
        """Get all files in this project with an extension."""
        return [x for x in self.files if x.extension == extension]

    @property
    def folder(self):
        """Get the relative path (relative to the media folder) of the project folder."""
        return os.path.join(
            os.path.join(settings.USER_DATA_FOLDER, self.user.username),
            self.name,
        )

    @property
    def files(self):
        """Get all files in of this project."""
        return File.objects.filter(project=self)

    def save(self, *args, **kwargs):
        """Save project."""
        Path(self.absolute_path).mkdir(parents=True, exist_ok=True)
        return super().save(*args, **kwargs)

    def clear_project_folder(self):
        """Clear the project folder and remove all File objects associated to it."""
        File.objects.filter(project=self).delete()
        remove_files_from_directory(self.absolute_path)

    def get_dictionary_files(self):
        """Get all dictionary files in this project (files ending with .dict)."""
        dictionary_file_formats = DictionaryFileFormat.objects.filter(
            pipeline=self.pipeline
        )
        return [
            x
            for x in self.files
            if DictionaryFileFormat.match_any(
                x.filename, dictionary_file_formats
            )
        ]

    def __str__(self):
        """Convert this object to string."""
        return self.name

    def has_extension_file(self, extensions):
        """
        Check if a file ends with some extension.

        :param extensions: a list of extensions that are valid.
        :param folder: the folder to check, if None this function uses self.folder
        :return: True if an .extension file is present with some text, False otherwise. Note: we may have multiple
        files, but as long as one is non empty we return true. (e.g. we have a.ext and b.ext, a is empty but b is not
        thus we return true).
        """
        for file in self.files:
            if file.extension in extensions:
                return True
        return False

    def finished_fa(self):
        """
        Check if FA has finished.

        :return: True if a .ctm file is present in the project directory, False otherwise
        """
        return self.has_extension_file(["ctm"])

    def create_downloadable_archive(self):
        """
        Create a downloadable archive.

        :return: the filename of the downloadable archive
        """
        zip_absolute_path = os.path.join(
            self.absolute_path, "{}.zip".format(self.name)
        )
        zip_obj = zipfile.ZipFile(zip_absolute_path, "w", zipfile.ZIP_DEFLATED)
        for file in self.files:
            zip_obj.write(file.absolute_file_path, file.filename)
        zip_obj.close()
        return zip_absolute_path

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


class File(models.Model):
    """File class for project."""

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        help_text="The Project this file belongs to.",
    )
    file = models.FileField(
        upload_to=project_folder_path,
        blank=False,
        null=False,
        unique=True,
        help_text="The file.",
    )

    @property
    def filename(self):
        """Get the filename."""
        return os.path.basename(self.file.name)

    @property
    def absolute_file_path(self):
        """Get the absolute path to the file."""
        return os.path.join(self.project.absolute_path, self.filename)

    @property
    def file_path(self):
        """Get the relative path (relative to the media folder) of the file."""
        return os.path.join(self.project.folder, self.file.name)

    @property
    def extension(self):
        """Get the extension of this file."""
        _, extension = os.path.splitext(self.filename)
        return extension[1:]

    @property
    def content(self):
        """Get the content of this file."""
        with self.file.open("r") as file:
            return file.read()

    def save(self, *args, **kwargs):
        """Save method."""
        # Remove the file object if it already exists
        if File.objects.filter(
            project=self.project, file=self.file_path
        ).exists():
            File.objects.get(project=self.project, file=self.file_path).delete()
        # Also remove the file such that the original filename is retained
        if os.path.exists(self.absolute_file_path):
            os.remove(self.absolute_file_path)
        return super().save(*args, **kwargs)

    def __str__(self):
        """Convert this object to string."""
        return self.filename
