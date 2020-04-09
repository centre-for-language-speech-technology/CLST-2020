from equestria.view_generic import *
from django.contrib.auth.mixins import LoginRequiredMixin


class WelcomePage(GenericTemplate):
    """Page to greet the user."""

    template_name = "welcome.html"


class PraatScripts(RestrictedTemplate):
    """Page to list all non-primary (praat) scripts."""

    template_name = "praat_scripts.html"


class UpdateDictionary(RestrictedTemplate):
    """Page to update dictionary."""

    template_name = "update_dictionary.html"


class AutoSegmentation(RestrictedTemplate):
    """Page to run auto-segmentation."""

    template_name = "auto_segmentation.html"
