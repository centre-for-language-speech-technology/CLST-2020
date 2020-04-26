import os
from django.core.exceptions import ValidationError


def validate_file_extension(value):
    # Ensures that files with other extensions cannot be uploaded
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = [".wav", ".txt", ".tg", ".zip"]
    if not ext.lower() in valid_extensions:
        raise ValidationError("Unsupported file extension.")
