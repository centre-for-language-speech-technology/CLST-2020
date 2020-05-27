from django.test import TestCase, Client
from django.urls import reverse, resolve
from scripts.models import Project
from upload.views import *


class TestUrls(TestCase):
    """Check if all defined urls resolve."""

    fixtures = ["uploadDB"]

    def setUp(self):
        """Set up the data needed to perform tests below."""
        self.project = Project.objects.filter(id=2)[0]
        self.url = reverse("upload:upload_project", args=[self.project])
        self.client = Client()

    def test_upload_page(self):
        """Check if upload resolves."""
        self.assertEqual(resolve(self.url).func.view_class, UploadProjectView)
        # self.assertEquals(resolve("/upload/2/upload", upload_file_view))
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
