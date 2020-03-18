from script_runner.models import InputTemplate
from script_runner.models import Script
from script_runner.constants import *
from script_runner.models import Process
from script_runner.models import Profile
import clam.common.client
import clam.common.data
import clam.common.status
import random
from urllib.parse import urlencode


def create_templates_from_data(inputtemplates):
    """Create template objects from data."""
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


def start_clam_server(profile, process_to_run, argument_files):
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
