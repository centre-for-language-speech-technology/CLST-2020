from django.test import TestCase
from scripts.models import Script, Pipeline, InputTemplate
import os
import multiprocessing
from django.core.exceptions import ValidationError
from unittest.mock import patch


class ScriptModelTest(TestCase):
    """Tests the script model."""

    fixtures = [
        "simple_pipelines.json",
    ]

    @staticmethod
    def _test(msg):
        """Debug method."""
        print(str(msg))
        os.system("dunstify {}".format(str(msg)))

    def setUp(self):
        """Get a script from the db for use in tests."""
        self.dfa = Script.objects.filter(id=1)[0]

    def tearDown(self):
        """Run after every test."""
        pass

    def test_number_of_scripts(self):
        """Test if scripts are loaded correctly."""
        self.assertEquals(len(Script.objects.all()), 3)

    def test_name(self):
        """Test if correct script is selected."""
        self.assertEquals(self.dfa.name, "Dutch Forced Alignment")

    def test_pipeline_name(self):
        """Test str method of pipeline."""
        name = "test_pipeline"
        self.pipeline = Pipeline.objects.create(
            name="test_pipeline", fa_script=self.dfa, g2p_script=self.dfa,
        )
        self.assertEquals(self.pipeline.__str__(), name)
        self.assertEquals(self.pipeline.fa_script, self.dfa)

    def test_input_template_name_unique_optional(self):
        """Test input template name when optional and unique."""
        self.input_template = InputTemplate.objects.create(
            template_id="123",
            format="txt",
            label="test",
            mime="text/plain",
            extension="txt",
            optional=True,
            unique=True,
            accept_archive=False,
            corresponding_profile=None,
        )
        name = "Unique optional file with extension txt"
        self.assertEquals(self.input_template.__str__(), name)

    def test_input_template_name_unique_not_optional(self):
        """Test input template name when not optional and unique."""
        self.input_template = InputTemplate.objects.create(
            template_id="123",
            format="txt",
            label="test",
            mime="text/plain",
            extension="txt",
            optional=False,
            unique=True,
            accept_archive=False,
            corresponding_profile=None,
        )
        name = "Unique file with extension txt"
        self.assertEquals(self.input_template.__str__(), name)

    def test_input_template_name_not_unique_optional(self):
        "Test input template name when optional and not unique."
        self.input_template = InputTemplate.objects.create(
            template_id="123",
            format="txt",
            label="test",
            mime="text/plain",
            extension="txt",
            optional=True,
            unique=False,
            accept_archive=False,
            corresponding_profile=None,
        )
        name = "Optional file with extension txt"
        self.assertEquals(self.input_template.__str__(), name)

    def test_input_template_name_not_unique_not_optional(self):
        "Test input template name when neither optional not unique."
        self.input_template = InputTemplate.objects.create(
            template_id="123",
            format="txt",
            label="test",
            mime="text/plain",
            extension="txt",
            optional=False,
            unique=False,
            accept_archive=False,
            corresponding_profile=None,
        )
        name = "File with extension txt"
        self.assertEquals(self.input_template.__str__(), name)

    @patch("os.listdir", return_value="")
    def test_input_template_is_valid_no_files_not_optional_not_unique(
        self, a=""
    ):
        """Test inputTemplate when no files."""
        self.input_template = InputTemplate.objects.create(
            template_id="123",
            format="txt",
            label="test",
            mime="text/plain",
            extension="txt",
            optional=False,
            unique=False,
            accept_archive=False,
            corresponding_profile=None,
        )
        self.assertEquals(self.input_template.is_valid("test"), False)

    @patch("os.listdir", return_value="")
    def test_input_template_is_valid_no_files_optional_not_unique(self, a=""):
        """Test for no files."""
        self.input_template = InputTemplate.objects.create(
            template_id="123",
            format="txt",
            label="test",
            mime="text/plain",
            extension="txt",
            optional=True,
            unique=False,
            accept_archive=False,
            corresponding_profile=None,
        )
        self.assertEquals(self.input_template.is_valid("test"), True)

    @patch("os.listdir", return_value=["a.txt", "b.txt"])
    def test_input_template_is_valid_some_files_not_optional_not_unique(
        self, a=""
    ):
        """Test with some files."""
        self.input_template = InputTemplate.objects.create(
            template_id="123",
            format="txt",
            label="test",
            mime="text/plain",
            extension="txt",
            optional=False,
            unique=False,
            accept_archive=False,
            corresponding_profile=None,
        )
        self.assertEquals(self.input_template.is_valid("test"), True)

    @patch("os.listdir", return_value=["a.txt", "b.txt"])
    def test_input_template_is_valid_some_files_not_optional_unique(self, a=""):
        """Test valid with some files and unique."""
        self.input_template = InputTemplate.objects.create(
            template_id="123",
            format="txt",
            label="test",
            mime="text/plain",
            extension="txt",
            optional=False,
            unique=True,
            accept_archive=False,
            corresponding_profile=None,
        )
        self.assertEquals(self.input_template.is_valid("test"), False)

    @patch("os.listdir", return_value=[])
    def test_input_template_is_valid_for_no_files_not_optional_not_unique(
        self, a=""
    ):
        """Test valid for no files."""
        self.input_template = InputTemplate.objects.create(
            template_id="123",
            format="txt",
            label="test",
            mime="text/plain",
            extension="txt",
            optional=False,
            unique=True,
            accept_archive=False,
            corresponding_profile=None,
        )
        self.assertEquals(self.input_template.is_valid_for("test"), False)

    @patch("os.listdir", return_value=["a.txt", "b.txt", "c.wav"])
    def test_input_template_is_valid_for_some_files_not_optional_not_unique(
        self, a=""
    ):
        """Test some files not optional not unique."""
        self.input_template = InputTemplate.objects.create(
            template_id="123",
            format="txt",
            label="test",
            mime="text/plain",
            extension="txt",
            optional=False,
            unique=False,
            accept_archive=False,
            corresponding_profile=None,
        )
        self.assertEquals(
            self.input_template.is_valid_for("test"), ["a.txt", "b.txt"]
        )
