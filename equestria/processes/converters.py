from django.urls.converters import IntConverter
from processes.models import Process


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
