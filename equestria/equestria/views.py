from django.http import HttpResponseRedirect
from django.urls import reverse
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
from equestria.view_generic import *


# Create your views here.


class WelcomePage(GenericTemplate):
    """Page to greet the user."""

    template_name = "welcome.html"


class PraatScripts(RestrictedTemplate):
    """Page to list all non-primary (praat) scripts."""

    template_name = "praat_scripts.html"


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
