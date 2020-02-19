from django.db import models
from django.conf import settings
import subprocess
import os


def execute_script():
    process = subprocess.Popen(['python3', os.path.join(settings.BASE_DIR, 'scripts/scriptje.py'), 'manage.py', 'bla'])
    Process.objects.create(process_id=process.pid, executing=True)
    print(process)


class Process(models.Model):
    process_id = models.IntegerField(blank=False)
    input_file = models.FilePathField(path=settings.FILE_PATH_FIELD_DIRECTORY)
    output_file = models.FilePathField(path=settings.FILE_PATH_FIELD_DIRECTORY)
    executing = models.BooleanField(default=False)
