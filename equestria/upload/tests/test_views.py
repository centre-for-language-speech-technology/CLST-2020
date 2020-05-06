from django.test import TestCase, Client
from django.urls import reverse, resolve
from scripts.models import Project
from equestria.views import *
from upload.views import *
from equestria.settings import BASE_DIR
import wave
import os
from unittest.mock import patch
from django.core.files.uploadedfile import SimpleUploadedFile


class TestView(TestCase):
    """Check the view."""

    fixtures = ["uploadDB"]

    def setUp(self):
        """Set up the data needed to perform tests below."""
        self.project = Project.objects.filter(id=2)[0]
        self.url = reverse("upload:upload_project", args=[self.project])
        self.client = Client()

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

        invalid_file = open(os.path.join(BASE_DIR, "test-files/test.xml"), "r")

        data = {"f": invalid_file}

        response = self.client.post(self.url, data, format="multipart")
        self.assertEqual(response.status_code, 302)
        # TODO: once implemented, we should check if the user gets a
        # warning that an invalid file is uploaded.

    @patch('upload.views.save_zipped_files')
    @patch('upload.views.save_file')
    def test_check_file_extension(self, mockSaveFile, mockZippFile):
        self.client.login(username="admin", password="admin")

        # mp4 is not allowed, thus we should not call any of the other extensions!
        file = SimpleUploadedFile("file.mp4", b"file_content", content_type="video/mp4")
        check_file_extension(self.project, file)
        assert(mockSaveFile.call_count == 0)
        assert (mockZippFile.call_count == 0)

        mockSaveFile.reset_mock()
        mockZippFile.reset_mock()

        file = SimpleUploadedFile("file.wav", b"file_content", content_type="video/mp4")
        check_file_extension(self.project, file)
        assert(mockSaveFile.call_count == 1)
        assert (mockZippFile.call_count == 0)

        # Quick test to see if reseting the mock works.
        mockSaveFile.reset_mock()
        mockZippFile.reset_mock()
        assert(mockSaveFile.call_count == 0)
        assert (mockZippFile.call_count == 0)

        file = SimpleUploadedFile("file.zip", b"file_content", content_type="video/mp4")
        check_file_extension(self.project, file)
        assert (mockSaveFile.call_count == 0)
        assert (mockZippFile.call_count == 1)


    def test_save_zipped_files(self):
        pass

    def test_save_file(self):
        pass