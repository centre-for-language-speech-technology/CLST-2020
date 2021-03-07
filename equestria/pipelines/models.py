import re

from django.db import models
from scripts.models import Script


class Pipeline(models.Model):
    """Pipeline model class."""

    name = models.CharField(
        max_length=512,
        help_text="The name of the Pipeline to appear to users when creating a new Project.",
    )
    fa_script = models.ForeignKey(
        Script,
        on_delete=models.PROTECT,
        blank=False,
        null=False,
        related_name="fa_script",
        help_text="The Forced Alignment Script to use for the Forced Alignment part of the Pipeline.",
    )
    g2p_script = models.ForeignKey(
        Script,
        on_delete=models.PROTECT,
        blank=False,
        null=False,
        related_name="g2p_script",
        help_text="The Grapheme to Phoneme Script to use for the Grapheme to Phoneme part of the Pipeline.",
    )

    def __str__(self):
        """
        Convert this object to a string.

        :return: the name property of this object
        """
        return self.name


class DictionaryFileFormat(models.Model):
    """Dictionary File Format."""

    pipeline = models.ForeignKey(
        Pipeline,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        help_text="The Pipeline for which to "
        "register the Dictionary File Format. Files that match the regular expression are shown in the"
        "Check Dictionary screen.",
    )
    regex = models.CharField(
        max_length=1024,
        null=False,
        blank=False,
        help_text="The regular expression to use when " "matching file names.",
    )

    def __init__(self, *args, **kwargs):
        """Initialize file preset."""
        super().__init__(*args, **kwargs)
        self._regex = re.compile(self.regex)

    @staticmethod
    def match_any(filename, dictionary_file_formats):
        """Match any filename against a list of DictionaryFileFormats."""
        for dictionary_file_format in dictionary_file_formats:
            if dictionary_file_format.match(filename):
                return True
        return False

    def match(self, filename):
        """Match a filename against this file preset."""
        return self._regex.match(filename)
