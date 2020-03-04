from django.db import models
from django.conf import settings
from django.urls import reverse
import subprocess
import os
import threading

# TODO: Set this in settings.py
DATABASE_FILE = "database.txt"


def spawn_wait_thread():
    process = subprocess.Popen(['python3', os.path.join(
        settings.BASE_DIR, 'scripts/scriptje.py'), 'manage.py', 'bla'])
    Process.objects.create(process_id=process.pid, status="starting")
    print(process)
    process.communicate()
    notify_process_done(process)


def execute_script():
    t1 = threading.Thread(target=spawn_wait_thread)
    t1.start()

def notify_process_done(process):
    print("Done")


class Process(models.Model):
    process_id = models.AutoField(primary_key=True)
    input_file = models.FilePathField(path=settings.FILE_PATH_FIELD_DIRECTORY, default="")
    output_file = models.FilePathField(path=settings.FILE_PATH_FIELD_DIRECTORY, default="")
    status = models.CharField(max_length=10, default="starting")


