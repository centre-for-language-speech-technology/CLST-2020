"""Module to define forms related to the upload app."""
from django import forms
from django.db import models


class UploadForm(forms.Form):
    """Form to upload file."""

    f = forms.FileField(
        widget=forms.ClearableFileInput(attrs={"multiple": True}),
        allow_empty_file=True,
    )
