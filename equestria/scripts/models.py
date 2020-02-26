from django.db import models
from django.conf import settings
import subprocess
import os
import threading


def spawn_wait_thread():
    process = subprocess.Popen(['python3', os.path.join(
        settings.BASE_DIR, 'scripts/scriptje.py'), 'manage.py', 'bla'])
    Process.objects.create(process_id=process.pid, executing=True)
    print(process)
    process.communicate()
    notify_process_done(process)


def notify_process_done(process):
    print("Process is done!")


# TODO we may need to pass some POST arguments later on.
# (that is why this function looks so empty)
def execute_script():
    t1 = threading.Thread(target=spawn_wait_thread)
    t1.start()


class Process(models.Model):
    process_id = models.IntegerField(blank=False)
    input_file = models.FilePathField(path=settings.FILE_PATH_FIELD_DIRECTORY)
    output_file = models.FilePathField(path=settings.FILE_PATH_FIELD_DIRECTORY)
    executing = models.BooleanField(default=False)
