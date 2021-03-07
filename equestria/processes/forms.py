import re
from django import forms
from django.core.exceptions import ValidationError
from processes.models import FilePreset, PreferableFile


class FilePresetAdminForm(forms.ModelForm):
    """Admin form for FilePresets."""

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

        model = FilePreset
        fields = "__all__"


class PreferableFileAdminForm(forms.ModelForm):
    """Admin form for FileDisplayRegex."""

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

        model = PreferableFile
        fields = "__all__"
