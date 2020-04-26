"""Module to define forms related to the upload app."""
from django import forms
from django.db import models
from .validator import validate_file_extension


class UploadForm(forms.Form):
    """Form to upload generic file."""

    f = forms.FileField(
        widget=forms.ClearableFileInput(attrs={"multiple": True}),
        allow_empty_file=True,
        validators=[validate_file_extension],
    )
