"""Module to define forms related to the upload app."""
from django import forms
from django.db import models
from .formExtension import ExtFileField


class UploadForm(forms.Form):
    """Form to upload files with file extension restriction."""

    f = ExtFileField(
        ext_whitelist=(".txt", ".tg", ".wav"),
        widget=forms.FileInput(attrs={"class": "custom-file-input"}),
    )


class UploadWAVForm(forms.Form):
    """Form to upload wav file."""

    wavFile = ExtFileField(
        ext_whitelist=(".wav", ".wav"),
        widget=forms.FileInput(attrs={"class": "custom-file-input"}),
    )
    # need duplicate in whitelist otherwise string will be treated as list and only valid filetypes are ".","w","a","v"
    # which does not make sense


class UploadFileForm(forms.Form):
    """Form to upload generic file."""

    title = forms.CharField(max_length=50)
    f = forms.FileField()
