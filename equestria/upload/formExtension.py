import os

from django import forms


class ExtFileField(forms.FileField):
    """
    Extend FileField with filetype restrictions.
    
    https://djangosnippets.org/snippets/977/ .

    This class was imported (https://djangosnippets.org/snippets/977/).
    Same as forms.FileField, but you can specify a file extension whitelist.
    
    >>> from django.core.files.uploadedfile import SimpleUploadedFile
    >>>
    >>> t = ExtFileField(ext_whitelist=(".pdf", ".txt"))
    >>>
    >>> t.clean(SimpleUploadedFile('filename.pdf', 'Some File Content'))
    >>> t.clean(SimpleUploadedFile('filename.txt', 'Some File Content'))
    >>>
    >>> t.clean(SimpleUploadedFile('filename.exe', 'Some File Content'))
    Traceback (most recent call last):
    ...
    ValidationError: [u'Not allowed filetype!']
    """

    def __init__(self, *args, **kwargs):
        """Initialize whitelist of allowed file extensions."""
        ext_whitelist = kwargs.pop("ext_whitelist")
        self.ext_whitelist = [i.lower() for i in ext_whitelist]

        super(ExtFileField, self).__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        """Check if uploaded file has allowed extension. Reject otherwise."""
        data = super(ExtFileField, self).clean(*args, **kwargs)
        if data:
            filename = data.name
            ext = os.path.splitext(filename)[1]
            ext = ext.lower()
            if ext not in self.ext_whitelist:
                raise forms.ValidationError(
                    "Filetype not allowed! Filetypes allowed: "
                    + ", ".join(self.ext_whitelist)
                )
        return data


if __name__ == "__main__":
    import doctest

    doctest.testmod()
