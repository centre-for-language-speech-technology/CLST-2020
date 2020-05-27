from unittest.mock import patch
from django.test import TestCase, Client
from scripts.services import *
import os
from equestria.settings.base import BASE_DIR


class TestServices(TestCase):
    """Check the view."""

    def setUp(self):
        """Set up the data needed to perform tests below."""
        pass

    @patch("zipfile.ZipFile")
    @patch("zipfile.ZipFile.close")
    @patch("zipfile.ZipFile.write")
    def test_zip_dir(self, mockZipw, mockZipc, mockzippie):
        file = os.path.join(BASE_DIR, "test-files/test.zip")
        zip_dir(os.path.join(BASE_DIR, "test-files"), file, ignore=None)

        assert mockZipw.call_count == 0
        assert mockZipc.call_count == 0
        assert mockzippie.call_count == 1
