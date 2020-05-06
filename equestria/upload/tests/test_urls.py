from django.test import TestCase, Client
from django.urls import reverse, resolve
from scripts.models import Project
from equestria.views import *
from upload.views import *
from equestria.settings import BASE_DIR
import wave
import os

class TestUrls(TestCase):
    """Check if all defined urls resolve."""
    fixtures = ["uploadDB"]

    def setUp(self):
        """Set up the data needed to perform tests below."""
        self.project = Project.objects.filter(id=2)[0]
        self.url = reverse("upload:upload_project", args=[self.project])
        self.client = Client()

    def name_resolves_to_class(self, view_name, view_class):
        """
        Test if a view with name view_name is resolved to view_class.
        
        :param view_name:  A name of a view, as defined by fancybar/views.py
        :param view_class: The class it should match
        """
        url = reverse(view_name)
        self.assertEquals(resolve(url).func.view_class, view_class)

    def test_upload_page(self):
        """Check if upload resolves."""
        self.assertEqual(resolve(self.url).func.view_class, UploadProjectView)
        #self.assertEquals(resolve("/upload/2/upload", upload_file_view))
        # self.name_resolves_to_class("welcome", WelcomePage)

    def test_redirect_before_auth(self):
        """Test whether redirection is working properly."""
        response = self.client.get(self.url, follow=True)
        redir_url = response.redirect_chain[0][0]
        redir_code = response.redirect_chain[0][1]
        self.assertRedirects(
            response,
            "/accounts/login/?next=/upload/2",
            status_code=302,
            target_status_code=200,
        )
        print(redir_url)
        self.assertEqual(redir_code, 302)
        self.assertEqual(redir_url, "/accounts/login/?next=/upload/2")

    def test_valid_file_ext_upload(self):
        """Test whether uploading valid files works properly."""

        self.client.login(username="admin", password="admin")

        audio_file = wave.open(
            os.path.join(BASE_DIR, "test-files/test.wav"), "rb"
        )
        data = {"f": audio_file}
        response = self.client.post(self.url, data, format="multipart")
        self.assertEqual(response.status_code, 302)

    def test_invalid_file_ext_upload(self):
        """Test whether uploading valid files fails properly."""
        self.client.login(username="admin", password="admin")

        invalid_file = open(
            os.path.join(BASE_DIR, "test-files/test.xml"), "r"
        )

        data = {"f": invalid_file}

        response = self.client.post(self.url, data, format="multipart")
        self.assertEqual(response.status_code, 302)
        # TODO: once implemented, we should check if the user gets a
        # warning that an invalid file is uploaded.
