from script_runner.models import (
    InputTemplate,
    Script,
    Process,
    Profile,
    STATUS_RUNNING,
    STATUS_DOWNLOAD,
    STATUS_FINISHED,
    STATUS_ERROR,
)
import clam.common.client
import clam.common.data
import clam.common.status
from django.conf import settings
from django.shortcuts import redirect
import secrets
import threading
import os


def start_project(project_name, script):
    random_token = secrets.token_hex(32)
    clamclient = clam.common.client.CLAMClient(script.hostname)
    clamclient.create(random_token)
    data = clamclient.get(random_token)
    process = Process.objects.create(
        name=project_name,
        script=Script.objects.get(pk=script.id),
        clam_id=random_token,
    )
    create_templates_from_data(process, data.inputtemplates())
    return process


def create_templates_from_data(process, inputtemplates):
    """Create template objects from data."""
    new_profile = Profile.objects.create(process=process)
    for input_template in inputtemplates:
        InputTemplate.objects.create(
            template_id=input_template.id,
            format=input_template.formatclass,
            label=input_template.label,
            extension=input_template.extension,
            optional=input_template.optional,
            unique=input_template.unique,
            accept_archive=input_template.acceptarchive,
            corresponding_profile=new_profile,
        )


def start_clam_server(profile, argument_files):
    """Add inputs and start a clam server."""
    process_to_run = Process.objects.get(pk=profile.process.id)
    clam_server = Script.objects.get(pk=process_to_run.script.id)
    clamclient = clam.common.client.CLAMClient(clam_server.hostname)
    for (file, template) in argument_files:
        clamclient.addinputfile(process_to_run.clam_id, template, file)

    clamclient.startsafe(process_to_run.clam_id)
    process_to_run.status = STATUS_RUNNING
    process_to_run.save()


def download_process(request):
    """Download process data."""
    # TODO: I adjusted this to a redirect, we have to change the method
    process_id = request.POST.get("process_id")
    return redirect("script_runner:process_download", process_id=process_id)


def update_script(process):
    if process.status == STATUS_RUNNING:
        associated_script = process.script
        clamclient = clam.common.client.CLAMClient(associated_script.hostname)
        try:
            data = clamclient.get(process.clam_id)
        except Exception as e:
            return None
        if data.status == clam.common.status.DONE:
            t = threading.Thread(target=download_output_files, args=(process,))
            t.start()
            process.status = STATUS_DOWNLOAD
            process.save()
        return data
    else:
        return None


def update_all_scripts():
    """
    Starts downloads for all the running scripts.

    :return: None
    """
    running_scripts = Process.objects.filter(status=STATUS_RUNNING)

    for process in running_scripts:
        update_script(process)


def download_output_files(process, format="zip"):
    """
    Download an output archive for a process.

    :param process: the process to download the archive for
    :param format: the format of the downloaded archive, either zip, gz or bz2
    :return: None
    """
    try:
        associated_script = process.script
        clamclient = clam.common.client.CLAMClient(associated_script.hostname)
        downloaded_archive = os.path.join(
            settings.DOWNLOAD_DIR, process.clam_id + ".{}".format(format)
        )
        clamclient.downloadarchive(process.clam_id, downloaded_archive, format)
        process.status = STATUS_FINISHED
        process.output_file = downloaded_archive
        process.save()
        clamclient.delete(process.clam_id)
    except Exception as e:
        print(e)
        process.status = STATUS_ERROR
        process.save()
