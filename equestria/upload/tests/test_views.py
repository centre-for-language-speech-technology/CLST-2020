from zipfile import BadZipFile

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
from django.core.files.storage import FileSystemStorage
import base64


class TestView(TestCase):
    """Check the view."""

    fixtures = ["uploadDB"]

    def setUp(self):
        """Set up the data needed to perform tests below."""
        self.project = Project.objects.filter(id=2)[0]
        self.url = reverse("upload:upload_project", args=[self.project])
        self.client = Client()

        # NOTE! this file must not be a zip file, or else other tests may fail.
        self.existing_file = SimpleUploadedFile(
            "existingFile.wav", b"file_content", content_type="video/wav"
        )
        path = self.project.folder
        fs = FileSystemStorage(location=path)
        #fs.save(self.existing_file.name, self.existing_file)

        # self.zipfile = zipfile.ZipFile(path + '/coolzip.zip', 'w')
        # f = open(path + "/acoolfile.txt", "w+")
        # f.write("Now the file looks even cooler.")
        # f.close()
        # self.zipfile.write(f.name, "coolfile.txt")

    def tearDown(self):
        pass
        # we created these files for testing, but we should remove it afterward to leave no traces behind.
        #path = self.project.folder
       # fs = FileSystemStorage(location=path)
      #  fs.delete(self.existing_file.name)
        # fs.delete(self.zipfile.filename)


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

    @patch("upload.views.save_zipped_files")
    @patch("upload.views.save_file")
    def test_check_file_extension(self, mockSaveFile, mockZippFile):
        self.client.login(username="admin", password="admin")

        # mp4 is not allowed, thus we should not call any of the other extensions!
        file = SimpleUploadedFile(
            "file.mp4", b"file_content", content_type="video/mp4"
        )
        check_file_extension(self.project, file)
        assert mockSaveFile.call_count == 0
        assert mockZippFile.call_count == 0

        mockSaveFile.reset_mock()
        mockZippFile.reset_mock()

        file = SimpleUploadedFile(
            "file.wav", b"file_content", content_type="video/mp4"
        )
        check_file_extension(self.project, file)
        assert mockSaveFile.call_count == 1
        assert mockZippFile.call_count == 0

        # Quick test to see if reseting the mock works.
        mockSaveFile.reset_mock()
        mockZippFile.reset_mock()
        assert mockSaveFile.call_count == 0
        assert mockZippFile.call_count == 0

        file = SimpleUploadedFile(
            "file.zip", b"file_content", content_type="video/mp4"
        )
        check_file_extension(self.project, file)
        assert mockSaveFile.call_count == 0
        assert mockZippFile.call_count == 1

    @patch("upload.views.check_file_extension")
    def test_save_zipped_files_fail(self, cfemock):
        try:
            save_zipped_files(self.project, self.existing_file)
            self.fail(
                "uploading a non zip file to save_zipped_files should fail..."
            )
        except BadZipFile:
            pass
        assert cfemock.call_count == 0

    @patch("upload.views.check_file_extension")
    def test_save_zipped_files(self, cfemock):
        file = SimpleUploadedFile(
            "coolzip.zip",
            base64.b64decode(
                "UEsDBBQACAAIALldmlAAAAAAAAAAABQAAAALACAAcGF5bG9hZC50eHRVVA0AB9/WpV4K16Ve39al\
XnV4CwABBOgDAAAE6AMAAFNITc7IV1DySM3JyVcIzy/KSVHiAgBQSwcIaHG+khYAAAAUAAAAUEsD\
BBQACAAIAMtdmlAAAAAAAAAAAA0AAAALACAAcGF5bG9hZC53YXZVVA0AB/7WpV4K16Ve/talXnV4\
CwABBOgDAAAE6AMAAEtNzshXUMowMspU4uICAFBLBwhuOur9DwAAAA0AAABQSwECFAMUAAgACAC5\
XZpQaHG+khYAAAAUAAAACwAgAAAAAAAAAAAApIEAAAAAcGF5bG9hZC50eHRVVA0AB9/WpV4K16Ve\
39alXnV4CwABBOgDAAAE6AMAAFBLAQIUAxQACAAIAMtdmlBuOur9DwAAAA0AAAALACAAAAAAAAAA\
AACkgW8AAABwYXlsb2FkLndhdlVUDQAH/talXgrXpV7+1qVedXgLAAEE6AMAAAToAwAAUEsFBgAA\
AAACAAIAsgAAANcAAAAAAA=="
            ),
            content_type="zip",
        )

        save_zipped_files(self.project, file)

        assert (
            cfemock.call_count == 2
        )  # The number of files in our mocking return value.

    @patch("django.core.files.storage.FileSystemStorage.save")
    @patch("django.core.files.storage.FileSystemStorage.delete")
    def test_save_file_new(self, fsDeleteMock, fsSaveMock):
        self.client.login(username="admin", password="admin")
        file = SimpleUploadedFile(
            "newFile.wav", b"file_content", content_type="video/mp4"
        )
        path = self.project.folder
        fs = FileSystemStorage(location=path)
        assert not fs.exists(file.name)
        save_file(self.project, file)
        assert fsDeleteMock.call_count == 0
        assert fsSaveMock.call_count == 1

    @patch("django.core.files.storage.FileSystemStorage.exists", return_value=True)
    @patch("django.core.files.storage.FileSystemStorage.save")
    @patch("django.core.files.storage.FileSystemStorage.delete")
    def test_save_file_existing(self, fsDeleteMock, fsSaveMock, fsExistsMock):
        self.client.login(username="admin", password="admin")
        save_file(self.project, self.existing_file)
        assert fsDeleteMock.call_count == 1
        assert fsSaveMock.call_count == 1
