from script_runner.models import InputTemplate, Script, Process, Profile
from script_runner.constants import *
import clam.common.client
import clam.common.data
import clam.common.status
import random
from urllib.parse import urlencode
from urllib.request import urlretrieve
from os.path import join, exists
from os import makedirs
from urllib.parse import urlencode
from django.shortcuts import render, redirect


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
    # TODO: If a file is already uploaded, uploading files over it gives an error, therefor we remove the
    # project and recreate it. There might be a better way of doing this in the future
    clamclient.delete(process_to_run.clam_id)
    clamclient.create(process_to_run.clam_id)
    for (file, template) in argument_files:
        clamclient.addinputfile(process_to_run.clam_id, template, file)

    clamclient.startsafe(process_to_run.clam_id)


def download_process(request):
    """Download process data."""
    process_id = request.POST.get("process_id")
    archive_type = request.POST.get("archive_type")
    clam_server = Script.objects.get(pk=1)
    clam_id = Process.objects.get(pk=process_id).clam_id
    if not exists("outputs"):
        makedirs("outputs")
        urlretrieve(
            "{}/{}/output?format=".format(
                clam_server.hostname, clam_id, archive_type
            ),
            join("outputs", "{}.{}".format(clam_id, archive_type)),
        )
        return redirect(
            "script_runner:clam",
            path="outputs/{}.{}".format(clam_id, archive_type),
        )
