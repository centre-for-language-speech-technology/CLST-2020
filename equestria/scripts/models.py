from django.db import models
from django.conf import settings
import subprocess
import os
import threading


PROC_STARTING = "starting"
PROC_RUNNING = "running"
PROC_STOPPED = "stopped"

# Starts a script
# process_id: The process_id as in the Process model, this id must be unique
# cmd: The script to run
# args: The arguments for the script in this format:
# dict(
#   parameter_name: parameter_value,
# )
# input_files: list with input file locations
def script_start(process_id, cmd, args, input_files):
    return True

# Returns the status of a script, either PROC_STARTING, PROC_RUNNING or PROC_STOPPED
def script_status(process_id):
    return PROC_STOPPED

# Kills a script
def script_kill(process_id):
    pass

# Returns a list containing all output files
def script_get_output_files(process_id):
    return []

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


