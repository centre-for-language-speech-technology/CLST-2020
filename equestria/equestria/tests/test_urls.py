from django.test import SimpleTestCase
from django.urls import reverse, resolve
from equestria.views import *
from scripts.views import *


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

    def test_home_page(self):
        """Check if homepage resolves."""
        self.name_resolves_to_class("welcome", WelcomePage)

    def test_forced_alignment_resolves(self):
        """Check if forced_alignment resolves."""
        self.name_resolves_to_class("scripts:projects", ProjectOverview)
