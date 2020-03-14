from django import forms


class UploadFileForm(forms.Form):
    """Form to upload generic file."""

    title = forms.CharField(max_length=50)
    f = forms.FileField()
