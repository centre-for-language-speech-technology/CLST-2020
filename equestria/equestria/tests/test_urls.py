from django.test import SimpleTestCase
from django.urls import reverse, resolve
from fancybar.views import *


class TestUrls(SimpleTestCase):
    """Check if all defined urls resolve."""

    def name_resolves_to_class(self, view_name, view_class):
        """
        Test if a view with name view_name is resolved to view_class.
        
        :param view_name:  A name of a view, as defined by fancybar/views.py
        :param view_class: The class it should match
        """
        url = reverse(view_name)
        self.assertEquals(resolve(url).func.view_class, view_class)

    def test_fancybar_resolves(self):
        """Check if fancybar resolves."""
        self.name_resolves_to_class("fancybar:fancybar", Fancybar)

    def test_praat_scripts_resolves(self):
        """Check if praat_scripts resolves."""
        self.name_resolves_to_class("fancybar:praat_scripts", PraatScripts)

    def test_upload_wav_resolves(self):
        """Check if upload_wav resolves."""
        self.name_resolves_to_class("fancybar:upload_wav", UploadWav)

    def test_upload_txt_resolves(self):
        """Check if upload_txt resolves."""
        self.name_resolves_to_class("fancybar:upload_txt", UploadTxt)

    def test_forced_alignment_resolves(self):
        """Check if forced_alignment resolves."""
        self.name_resolves_to_class(
            "fancybar:forced_alignment", ForcedAlignment
        )

    def test_update_dictionary_resolves(self):
        """Check if update_dictionary resolves."""
        self.name_resolves_to_class(
            "fancybar:update_dictionary", UpdateDictionary
        )

    def test_auto_segmentation_resolves(self):
        """Check if auto_segmentation resolves."""
        self.name_resolves_to_class(
            "fancybar:auto_segmentation", AutoSegmentation
        )

    def test_download_results_resolves(self):
        """Check if download_results resolves."""
        self.name_resolves_to_class(
            "fancybar:download_results", DownloadResults
        )
