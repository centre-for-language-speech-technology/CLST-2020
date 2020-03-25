from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from scripts.models import Script, Argument
from django.core.files.storage import FileSystemStorage
from upload import forms as uploadForms
from scripts.constants import *

# from scripts import backend_interface
# from scripts.backend_interface import ClamConfiguration
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.conf import settings
from scripts.models import Process
from scripts.models import Profile
from scripts.models import InputTemplate
import clam.common.client
import clam.common.data
import clam.common.status
import random
from urllib.request import urlretrieve
from os.path import join, exists
from os import makedirs
from urllib.parse import urlencode
from scripts.clamhelper import (
    create_templates_from_data,
    start_clam_server,
)


# Create your views here.


class GenericTemplate(TemplateView):
    """View to render a html page without any additional features."""

    template_name = "template.html"

    def __get_profile(self, request):
        """Retrieve profile based on user in request."""
        user_profile = (
            UserProfile.objects.select_related()
            .filter(user_id=request.user.id)
            .first()
        )
        return user_profile

    def get(self, request):
        """Respond to get request."""
        return render(request, self.template_name)

    def post(self, request):
        """Respond to post request."""
        return render(request, self.template_name)


class RestrictedTemplate(TemplateView):
    """View to render a html page without any additional features that is login restricted."""

    template_name = "template.html"

    def __get_profile(self, request):
        """Retrieve profile based on user in request."""
        user_profile = (
            UserProfile.objects.select_related()
            .filter(user_id=request.user.id)
            .first()
        )
        return user_profile

    def get(self, request):
        """Respond to get request."""
        if not request.user.is_authenticated:
            return redirect("%s?next=%s" % (settings.LOGIN_URL, request.path))
        else:
            return render(request, self.template_name)

    def post(self, request):
        """Respond to post request."""
        if not request.user.is_authenticated:
            return redirect("%s?next=%s" % (settings.LOGIN_URL, request.path))
        else:
            return render(request, self.template_name)


class WelcomePage(GenericTemplate):
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
        "profile": None,
    }

    def __get_profile(self, request):
        """Retrieve profile based on user in request."""
        user_profile = (
            UserProfile.objects.select_related()
            .filter(user_id=request.user.id)
            .first()
        )
        return user_profile

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

    def __filter_arguments(self, request):
        """Filter relevant arguments from post request."""
        args = []
        for argument in Argument.objects.select_related().filter(
            associated_script=script_id
        ):
            args += [
                (
                    argument,
                    request.POST.get(
                        "script_{}_argument_{}".format(script_id, argument.id)
                    ),
                ),
            ]
        return args

    def get(self, request):
        """Respond to get request."""
        if not request.user.is_authenticated:
            return redirect("%s?next=%s" % (settings.LOGIN_URL, request.path))
        else:
            return render(request, self.template_name, self.arg)

    def post(self, request):
        """Process command line arguments and run selected script."""
        if not request.user.is_authenticated:
            return redirect("%s?next=%s" % (settings.LOGIN_URL, request.path))
        else:
            if request.POST.get("form_handler") == "create_project":
                # TODO: Change this
                clamclient = clam.common.client.CLAMClient(
                    "http://localhost:8080"
                )
                project_name = str(random.getrandbits(64))
                clamclient.create(project_name)
                data = clamclient.get(project_name)
                process = Process.objects.create(
                    name="new process",
                    script=Script.objects.get(pk=1),
                    clam_id=project_name,
                )
                create_templates_from_data(process, data.inputtemplates())
                return render(request, self.template_name, self.arg)
            elif request.POST.get("form_handler") == "run_profile":
                profile_id = request.POST.get("profile_id")
                profile = Profile.objects.get(pk=profile_id)
                argument_files = list()
                for (
                    input_template
                ) in InputTemplate.objects.select_related().filter(
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
                                        "template_id_{}".format(
                                            input_template.id
                                        )
                                    ].name,
                                    input_template.template_id,
                                )
                            )

                            start_clam_server(profile, argument_files)

                            return render(request, self.template_name, self.arg)
            elif request.POST.get("form_handler") == "download_process":
                return download_output_files(request)


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
        if not request.user.is_authenticated:
            return redirect("%s?next=%s" % (settings.LOGIN_URL, request.path))
        else:
            form = uploadForms.UploadFileForm()
            return render(request, self.template_name, self.arg)

    def post(self, request):
        """Save uploaded files. TODO: Does not yet run anything."""
        if not request.user.is_authenticated:
            return redirect("%s?next=%s" % (settings.LOGIN_URL, request.path))
        else:
            return render(request, self.template_name, self.arg)


class UpdateDictionary(RestrictedTemplate):
    """Page to update dictionary."""

    template_name = "update_dictionary.html"


class AutoSegmentation(RestrictedTemplate):
    """Page to run auto-segmentation."""

    template_name = "auto_segmentation.html"


class DownloadResults(RestrictedTemplate):
    """Page to download results. TODO: Discuss if needed."""

    template_name = "download_results.html"
