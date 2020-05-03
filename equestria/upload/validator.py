import os
from django.core.exceptions import ValidationError


def validate_file_extension(file):
    """
    Check if the file extension is in the whitelist.

    :param file: the file to be validated
    :param file: the file to be uploaded
    :return: None
    """
    ext = os.path.splitext(file.name)[1]  # [0] returns path+filename
    valid_extensions = [".wav", ".txt", ".tg", ".zip"]
    if not ext.lower() in valid_extensions:
        raise ValidationError("Unsupported file extension.")
