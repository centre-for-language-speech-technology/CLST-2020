from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from script_runner.models import Script, Argument
from django.core.files.storage import FileSystemStorage
from upload import forms as uploadForms
from script_runner.constants import *
from script_runner.models import Process
from script_runner.models import Profile
from script_runner.models import InputTemplate
import clam.common.client
import clam.common.data
import clam.common.status
import random
from urllib.request import urlretrieve


# Create your views here.


class GenericTemplate(TemplateView):
    """View to render a html page without any additional features."""

    template_name = "template.html"

    def get(self, request):
        """Respond to get request."""
        return render(request, self.template_name)

    def post(self, request):
        """Respond to post request."""
        return render(request, self.template_name)


class Fancybar(GenericTemplate):
    """Legacy template for demo and testing purposes."""

    template_name = "template.html"


class PraatScripts(TemplateView):
    """Page to list all non-primary (praat) scripts."""

    template_name = "praat_scripts.html"

    arg = {
        "scripts": None,
        "USER_SPECIFIED_FILE": USER_SPECIFIED_FILE,
        "USER_SPECIFIED_TEXT": USER_SPECIFIED_TEXT,
        "USER_SPECIFIED_BOOL": USER_SPECIFIED_BOOL,
        "USER_SPECIFIED_INT": USER_SPECIFIED_INT,
    }

    def __init__(self, **kwargs):
        """Load all script from the database."""
        super().__init__(**kwargs)
        self.arg["processes"] = Process.objects.all()

        for process in self.arg["processes"]:
            process.profiles = Profile.objects.select_related().filter(
                process=process.id
            )
            for profile in process.profiles:
                profile.input_templates = InputTemplate.objects.select_related().filter(
                    corresponding_profile=profile.id
                )

    def get(self, request):
        """Respond to get request."""
        return render(request, self.template_name, self.arg)

    def post(self, request):
        """Process command line arguments and run selected script."""
        self.arg["download_in_progress"] = False
        if request.POST.get("form_handler") == "create_project":
            # TODO: Change this
            clamclient = clam.common.client.CLAMClient("http://localhost:8080")
            project_name = str(random.getrandbits(64))
            clamclient.create(project_name)
            data = clamclient.get(project_name)
            process = Process.objects.create(
                name="new process",
                script=Script.objects.get(pk=1),
                clam_id=project_name,
            )
            new_profile = Profile.objects.create(process=process)
            for input_template in data.inputtemplates():
                InputTemplate.objects.create(
                    template_id=input_template.id,
                    format=input_template.formatclass,
                    mime=input_template.formatclass.mimetype,
                    label=input_template.label,
                    extension=input_template.extension,
                    optional=input_template.optional,
                    unique=input_template.unique,
                    accept_archive=input_template.acceptarchive,
                    corresponding_profile=new_profile,
                )
            return render(request, self.template_name, self.arg)
        elif request.POST.get("form_handler") == "run_profile":
            profile_id = request.POST.get("profile_id")
            profile = Profile.objects.get(pk=profile_id)
            argument_files = list()
            for input_template in InputTemplate.objects.select_related().filter(
                corresponding_profile=profile
            ):
                # TODO: This is now writing to the main directory, replace this with files from the uploaded files
                with open(
                    request.FILES[
                        "template_id_{}".format(input_template.id)
                    ].name,
                    "wb",
                ) as file:
                    for chunk in request.FILES[
                        "template_id_{}".format(input_template.id)
                    ]:
                        file.write(chunk)
                argument_files.append(
                    (
                        request.FILES[
                            "template_id_{}".format(input_template.id)
                        ].name,
                        input_template.template_id,
                    )
                )

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

            return render(request, self.template_name, self.arg)
        elif request.POST.get("form_handler") == "download_process":
            process_id = request.POST.get("process_id")
            archive_type = request.POST.get("archive_type")
            clam_server = Script.objects.get(pk=process_id)
            clam_id = Process.objects.get(pk=process_id).clam_id
            urlretrieve(
                "{}/{}/output?format=".format(
                    clam_server.hostname, clam_id, archive_type
                ),
                "outputs/{}.{}".format(clam_id, archive_type),
            )
            return redirect(
                "script_runner:downloads",
                path="outputs/{}.{}".format(clam_id, archive_type),
            )


class UploadWav(GenericTemplate):
    """Legacy file for uploading wav files. No loner necessary. TODO: Martin remove pls."""

    template_name = "upload_wav.html"


class UploadTxt(GenericTemplate):
    """Legacy file for uploading txt files. No loner necessary. TODO: Martin remove pls."""

    template_name = "upload_txt.html"


class ForcedAlignment(TemplateView):
    """Page to run main forced alignment script. Contains two upload forms for txt and wav files."""

    template_name = "forced_alignment.html"

    """
    TODO: Why are there two get methods here?
    def get(self, request):
        return render(request, self.template_name)
    """

    def get(self, request):
        """Responds to get request and loads upload forms."""
        form = uploadForms.UploadFileForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        """Save uploaded files. TODO: Does not yet run anything."""
        form = uploadForms.UploadFileForm(request.POST, request.FILES)
        f = request.FILES["f"]
        fs = FileSystemStorage()
        fs.save(f.name, f)
        # TODO: execute script
        return render(request, self.template_name)


class UpdateDictionary(GenericTemplate):
    """Page to update dictionary."""

    template_name = "update_dictionary.html"


class AutoSegmentation(GenericTemplate):
    """Page to run auto-segmentation."""

    template_name = "auto_segmentation.html"


class DownloadResults(GenericTemplate):
    """Page to download results. TODO: Discuss if needed."""

    template_name = "download_results.html"

    template_name = "download_results.html"
