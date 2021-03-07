import re
from .models import DictionaryFileFormat
from django import forms
from django.core.exceptions import ValidationError


class DictionaryFileFormatAdminForm(forms.ModelForm):
    """Admin form for DictionaryFileFormat."""

    def clean_regex(self):
        """Clean regex."""
        regex = self.cleaned_data.get("regex")
        try:
            re.compile(regex)
            return regex
        except re.error as e:
            raise ValidationError(
                "The regex is incorrect and returned the following error: {}".format(
                    e
                )
            )

    class Meta:
        """Meta class."""

        model = DictionaryFileFormat
        fields = "__all__"
