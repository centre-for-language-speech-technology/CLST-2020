from zipfile import BadZipFile

from django.test import TestCase, Client
from django.urls import reverse
from scripts.models import Project
from upload.views import *

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
            "existingFile.wav", b"file_content", content_type="wav"
        )
        self.invalid_file = SimpleUploadedFile(
            "invalid.xml", b"file_content", content_type="xml"
        )

    @patch("os.listdir", return_value=["test.wav"])
    def test_get(self, mock):
        """Test a get request as admin."""
        self.client.login(username="admin", password="admin")

        data = {"f": self.existing_file}
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, 200)
        print(mock.call_count)  # just for CI deadcode failing here

    @patch("os.listdir", return_value=["test.wav"])
    def test_get2(self, listdirMock):
        """Test a GET request with single wav file."""

        self.client.login(username="admin", password="admin")

        data = {"f": self.existing_file}
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, 200)
        print(listdirMock.call_count)  # just for CI deadcode failing here

    @patch("os.listdir", return_value=["test.wav"])
    def test_POST1(self, mock):
        """Test whether uploading valid files works properly."""

        self.client.login(username="admin", password="admin")

        data = {"f": self.existing_file}
        response = self.client.post(self.url, data, format="multipart")
        self.assertEqual(response.status_code, 302)
        print(mock.call_count)  # just for CI deadcode failing here

    @patch("os.listdir", return_value=["test.wav"])
    @patch("scripts.models.Project.can_start_new_process", return_value=False)
    def test_POST2(self, can_start_new_mock, mock):
        """Test whether uploading valid files works properly and starts new process."""
        self.client.login(username="admin", password="admin")
        data = {"f": self.existing_file}
        response = self.client.post(self.url, data, format="multipart")
        self.assertEqual(response.status_code, 200)
        print(can_start_new_mock.call_count)  # Just for Ci deadcode analysis.
        print(mock.call_count)  # just for CI deadcode failing here

    def test_invalid_file_ext_upload(self):
        """Test whether uploading valid files fails properly."""
        self.client.login(username="admin", password="admin")

        data = {"f": self.invalid_file}

        response = self.client.post(self.url, data, format="multipart")
        self.assertEqual(response.status_code, 302)
        # TODO: once implemented, we should check if the user gets a
        # warning that an invalid file is uploaded.

    @patch("upload.views.save_zipped_files")
    @patch("upload.views.save_file")
    def test_check_file_extension(self, mockSaveFile, mockZippFile):
        """Test if file extension check works."""

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
        """Test if saving zipped files fails if uploading non zip file."""
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
        """Test if zip file upload works."""
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
        """Test if saving a new file works."""

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

    @patch(
        "django.core.files.storage.FileSystemStorage.exists", return_value=True
    )
    @patch("django.core.files.storage.FileSystemStorage.save")
    @patch("django.core.files.storage.FileSystemStorage.delete")
    def test_save_file_existing(self, fsDeleteMock, fsSaveMock, fsExistsMock):
        """Test if saving existing files work."""

        self.client.login(username="admin", password="admin")
        save_file(self.project, self.existing_file)
        assert fsDeleteMock.call_count == 1
        assert fsSaveMock.call_count == 1
        assert fsExistsMock.call_count == 1
