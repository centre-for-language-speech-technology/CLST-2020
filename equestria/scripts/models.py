from django.db import models
from django.conf import settings
import subprocess
import os

# Create your models here.

def execute_script():
    subprocess.call(['python3', os.path.join(settings.BASE_DIR, 'scripts/scriptje.py'), 'manage.py', 'bla'])

class Process(models.Model):

    process_id = models.IntegerField()
    input_file = models.FilePathField(path=settings.FILE_PATH_FIELD_DIRECTORY)
    output_file = models.FilePathField(path=settings.FILE_PATH_FIELD_DIRECTORY)
    executing = models.BooleanField()

