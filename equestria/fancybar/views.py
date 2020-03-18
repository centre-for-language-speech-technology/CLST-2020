from django.views.generic import TemplateView
from django.shortcuts import render
from script_runner.models import Script, Argument
from accounts.models import UserProfile
from django.core.files.storage import FileSystemStorage
from upload import forms as uploadForms
from script_runner.constants import *
from script_runner import backend_interface
from script_runner.backend_interface import ClamConfiguration


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
        self.arg["scripts"] = Script.objects.all()

        for s in self.arg["scripts"]:
            s.args = Argument.objects.select_related().filter(
                associated_script=s.id
            )

    def get(self, request):
        """Respond to get request."""
        self.arg["profile"] = self.__get_profile(request)
        return render(request, self.template_name, self.arg)

    def post(self, request):
        """Process command line arguments and run selected script."""
        name = request.POST.get("script_name", "")
        arg["profile"] = self.__get_profile(request)
        script_id = request.POST.get("script_id", "")
        args = self.__filter_arguments(request)
        self.__run_and_log_script(script_id, args)
        self.arg["script_run"] = name
        return render(request, self.template_name, self.arg)

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

    def __run_and_log_script(self, script_id, args):
        """Pass script to backend for execution and print debug info."""
        print('"Running" script ' + name + "...")
        print(args)
        script = Script.objects.get(pk=script_id)
        backend_interface.run(script, args)


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
