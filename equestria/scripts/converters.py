from django.urls.converters import IntConverter
from .models import Project, Profile, Process, Script


class ScriptConverter(IntConverter):
    """Converter for Script model."""

    def to_python(self, value):
        """
        Cast integer to Script.

        :param value: the public key of the Script
        :return: a Script or ValueError
        """
        try:
            return Script.objects.get(id=int(value))
        except Script.DoesNotExist:
            raise ValueError

    def to_url(self, obj):
        """
        Cast an object of Script to a string.

        :param obj: the Script object
        :return: the public key of the Script object in string format
        """
        return str(obj.pk)


class ProjectConverter(IntConverter):
    """Converter for Project model."""

    def to_python(self, value):
        """
        Cast integer to Project.

        :param value: the public key of the Project
        :return: a Project or ValueError
        """
        try:
            return Project.objects.get(id=int(value))
        except Project.DoesNotExist:
            raise ValueError

    def to_url(self, obj):
        """
        Cast an object of Project to a string.

        :param obj: the Project object
        :return: the public key of the Project object in string format
        """
        return str(obj.pk)


class ProfileConverter(IntConverter):
    """Converter for Profile model."""

    def to_python(self, value):
        """
        Cast integer to Profile.

        :param value: the public key of the Profile
        :return: a Profile or ValueError
        """
        try:
            return Profile.objects.get(id=int(value))
        except Profile.DoesNotExist:
            raise ValueError

    def to_url(self, obj):
        """
        Cast an object of Profile to a string.

        :param obj: the Profile object
        :return: the public key of the Profile object in string format
        """
        return str(obj.pk)


class ProcessConverter(IntConverter):
    """Converter for Process model."""

    def to_python(self, value):
        """
        Cast integer to Process.

        :param value: the public key of the Process
        :return: a Process or ValueError
        """
        try:
            return Process.objects.get(id=int(value))
        except Process.DoesNotExist:
            raise ValueError

    def to_url(self, obj):
        """
        Cast an object of Process to a string.

        :param obj: the Process object
        :return: the public key of the Process object in string format
        """
        return str(obj.pk)
