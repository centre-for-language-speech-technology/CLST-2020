from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse


class GenericViewTest(TestCase):
    """Defines utility methods for testing views."""

    default_templates = ["progbase.html", "base.html", "pipeline.html"]
    name = ""  # name of url as defined in urls.py

    def setUp(self):
        """Initialize response before every test."""
        self.client = Client()
        self.response = self.client.get(reverse(self.name))

    def get_uses_templates(self, templates):
        """
        Check if GET on url with name is rendered successfully using templates.

        Every file in templates needs to be used to render
        The view may also use additional unspecified files
        :param templates: list of template files that render request
        """
        self.assertEquals(self.response.status_code, 200)
        for template in templates:
            self.assertTemplateUsed(self.response, template)

    def get_uses_template_and_defaults(self, template):
        """
        Check if GET on url with name is rendered successfully using template and default templates.

        The view may also use additional unspecified files
        :param template: template file that renders request
        """
        self.get_uses_templates([template,] + self.default_templates)


class RestrictedViewTest(GenericViewTest):
    """Defines utility methods for testing login restricted views."""

    def redirects_to_login(self):
        """Test a GET request without login. Expect to be redirected."""
        self.assertEquals(self.response.status_code, 302)
        # Frontend isn't using any templates as it seems
        # self.assertTemplateUsed(response, "login.html")

    def login(self):
        """Log in a test user."""
        username = "testuser"
        secret = "my_favorite_pony_is_cozy_glow_but_dont_tell_anyone_its_kinda_embarrasing"
        """Delete the userdb to ensure unique usernames."""
        User.objects.all().delete()
        User.objects.create_user(username=username, password=secret)
        success = self.client.login(username=username, password=secret)
        self.assertTrue(success)

    def get_uses_templates(self, templates):
        """
        Check if GET on url with name is rendered successfully using templates.

        Every file in templates needs to be used to render
        The view may also use additional unspecified files
        :param templates: list of template files that render request
        """
        self.login()
        self.response = self.client.get(reverse(self.name))
        super().get_uses_templates(templates)

    def get_uses_template_and_defaults(self, template):
        """
        Check if GET on url with name is rendered successfully using template and default templates.

        The view may also use additional unspecified files
        :param template: template file that renders request
        """
        self.login()
        self.response = self.client.get(reverse(self.name))
        super().get_uses_template_and_defaults(template)


class TestLoginSystem(RestrictedViewTest):
    """Test login system related features."""

    name = "accounts:login"

    def test_login(self):
        """Test whether login works."""
        # self.assertFalse(self.response.user.is_authenticated())
        # self.login()
        # self.response = self.client.get(reverse(self.name))
        # self.assertTrue(self.response.user.is_authenticated())


class TestPraatScripts(RestrictedViewTest):
    """Test the PraatScripts view."""

    name = "praat_scripts"

    def test_get(self):
        """Test a get request."""
        self.redirects_to_login()
        self.login()
        self.get_uses_template_and_defaults("praat_scripts.html")


class TestForcedAlignment(RestrictedViewTest):
    """Test the ForcedAlignment view."""

    name = "scripts:projects"

    def test_get(self):
        """Test a get request."""
        self.redirects_to_login()
        self.login()
        self.get_uses_template_and_defaults("scripts/project-overview.html")


class TestUpdateDictionary(RestrictedViewTest):
    """Test the UpdateDictionary view."""

    name = "update_dictionary"

    def test_get(self):
        """Test a get request."""
        self.redirects_to_login()
        self.login()
        self.get_uses_template_and_defaults("update_dictionary.html")


class TestAutoSegmentation(RestrictedViewTest):
    """Test the AutoSegmentation view."""

    name = "auto_segmentation"

    def test_get(self):
        """Test a get request."""
        self.redirects_to_login()
        self.login()
        self.get_uses_template_and_defaults("auto_segmentation.html")
