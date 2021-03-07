from django.urls.converters import IntConverter
from .models import Profile, Script


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
