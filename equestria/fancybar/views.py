from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from script_runner.models import Script
from upload import forms as uploadForms
from script_runner.constants import *
from script_runner.models import Process
from script_runner.models import Profile
from script_runner.models import InputTemplate
import clam.common.client
import clam.common.data
import clam.common.status
import random
from urllib.parse import urlencode


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
        if request.POST.get("form_handler",) == "create_project":
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
                    label=input_template.label,
                    extension=input_template.extension,
                    optional=input_template.optional,
                    unique=input_template.unique,
                    accept_archive=input_template.acceptarchive,
                    corresponding_profile=new_profile,
                )
            return render(request, self.template_name, self.arg)
        elif request.POST.get("form_handler",) == "run_profile":
            profile_id = request.POST.get("profile_id",)
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


class UploadWav(GenericTemplate):
    """Legacy file for uploading wav files. No loner necessary. TODO: Martin remove pls."""

    template_name = "upload_wav.html"


class UploadTxt(GenericTemplate):
    """Legacy file for uploading txt files. No loner necessary. TODO: Martin remove pls."""

    template_name = "upload_txt.html"


class ForcedAlignment(TemplateView):
    """Page to run main forced alignment script. Contains two upload forms for txt and wav files."""

    template_name = "forced_alignment.html"
    arg = dict()

    def __init__(self, **kwargs):
        """Load all script from the database."""
        super().__init__(**kwargs)
        self.arg["scripts"] = Script.objects.select_related().filter(
            forced_alignment_script=True
        )

    """
    TODO: Why are there two get methods here?
    def get(self, request):
        return render(request, self.template_name)
    """

    def get(self, request):
        """Responds to get request and loads upload forms."""
        form = uploadForms.UploadFileForm()
        return render(request, self.template_name, self.arg)

    def post(self, request):
        """Save uploaded files. TODO: Does not yet run anything."""
        if request.POST.get("form_handler",) == "create_project":
            script_id = request.POST.get("script_id",)
            clamclient = clam.common.client.CLAMClient("http://localhost:8080")
            # TODO: This should later on be something like [username]_[project_name]
            project_name = request.POST.get("project_name",)
            clamclient.create(project_name)
            data = clamclient.get(project_name)
            process = Process.objects.create(
                name=project_name,
                script=Script.objects.get(pk=script_id),
                clam_id=project_name,
            )
            new_profile = Profile.objects.create(process=process)
            for input_template in data.inputtemplates():
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
            return redirect_with_parameters(
                "script_runner:process",
                process.id,
                redirect="fancybar:update_dictionary",
            )
        return render(request, self.template_name, self.arg)


class UpdateDictionary(GenericTemplate):
    """Page to update dictionary."""

    template_name = "update_dictionary.html"


class AutoSegmentation(GenericTemplate):
    """Page to run auto-segmentation."""

    template_name = "auto_segmentation.html"


class DownloadResults(GenericTemplate):
    """Page to download results. TODO: Discuss if needed."""

    template_name = "download_results.html"


def redirect_with_parameters(url_name, *args, **kwargs):
    """
    Redirects to a page with GET parameters specified in kwargs.

    :param url_name: the url to redirect to (reverse will get called on this string)
    :param args: the arguments for reverse in the url
    :param kwargs: the GET parameters
    :return: HttpResponseRedirect with the asked url
    """
    url = reverse(url_name, args=args)
    params = urlencode(kwargs)
    return HttpResponseRedirect(url + "?%s" % params)
