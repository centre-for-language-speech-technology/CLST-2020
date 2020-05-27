from django.test import TestCase
from scripts.models import (
    Script,
    Pipeline,
    InputTemplate,
    IntegerParameter,
    BaseParameter,
    FloatParameter,
    TextParameter,
    StringParameter,
)
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

    def test_integer_parameter(self):
        """Test if get_value works."""
        ip = IntegerParameter(base=None, value=1)
        self.assertEquals(1, ip.get_value())

    def test_ip_get_corresponding_value_good(self):
        """Test if get_corresponding_value works in good case."""
        ip = IntegerParameter(base=None, value=1)
        self.assertEquals(1, ip.get_corresponding_value(1))

    def test_ip_get_corresponding_value_bad(self):
        """Test if get_corresponding_value works in bad case."""
        ip = IntegerParameter(base=None, value="cookie")
        self.assertEquals(None, ip.get_corresponding_value("cookie"))

    def test_ip_set_preset(self):
        """Tests set preset."""
        bp = BaseParameter(
            name="test", corresponding_script=None, preset=False, type=1
        )
        ip = IntegerParameter(base=bp, value="cookie")

        ip.set_preset(3)
        self.assertEquals(3, ip.get_value())
        self.assertEquals(3, ip.value)

    def test_float_parameter(self):
        """Test if get_value works."""
        fp = FloatParameter(base=None, value=1.3)
        self.assertEquals(1.3, fp.get_value())

    def test_fp_get_corresponding_value_good(self):
        """Test if get_corresponding_value works in good case."""
        fp = FloatParameter(base=None, value=1.3)
        self.assertEquals(1.3, fp.get_corresponding_value(1.3))

    def test_fp_get_corresponding_value_bad(self):
        """Test if get_corresponding_value works in bad case."""
        fp = FloatParameter(base=None, value="cookie")
        self.assertEquals(None, fp.get_corresponding_value("cookie"))

    def test_fp_set_preset(self):
        """Tests set preset."""
        bp = BaseParameter(
            name="test", corresponding_script=None, preset=False, type=1
        )
        fp = FloatParameter(base=bp, value="cookie")

        fp.set_preset(4.2)
        self.assertEquals(4.2, fp.get_value())
        self.assertEquals(4.2, fp.value)

    def test_text_parameter(self):
        """Test if get_value works."""
        tp = TextParameter(base=None, value="asdf")
        self.assertEquals("asdf", tp.get_value())

    def test_tp_get_corresponding_value_good(self):
        """Test if get_corresponding_value works in good case."""
        tp = TextParameter(base=None, value="Olaf")
        self.assertEquals("Stitch", tp.get_corresponding_value("Stitch"))

    def test_tp_get_corresponding_value_bad(self):
        """Test if get_corresponding_value works in bad case."""
        tp = TextParameter(base=None, value=6.9)
        self.assertEquals(None, tp.get_corresponding_value(6.9))

    def test_tp_set_preset(self):
        """Tests set preset."""
        bp = BaseParameter(
            name="test", corresponding_script=None, preset=False, type=1
        )
        tp = TextParameter(base=bp, value="cookie")

        tp.set_preset("Fluttershy")
        self.assertEquals("Fluttershy", tp.get_value())
        self.assertEquals("Fluttershy", tp.value)

    def test_string_parameter(self):
        """Test if get_value works."""
        sp = StringParameter(base=None, value="asdf")
        self.assertEquals("asdf", sp.get_value())

    def test_sp_get_corresponding_value_good(self):
        """Test if get_corresponding_value works in good case."""
        sp = StringParameter(base=None, value="Olaf")
        self.assertEquals("Stitch", sp.get_corresponding_value("Stitch"))

    def test_sp_get_corresponding_value_bad(self):
        """Test if get_corresponding_value works in bad case."""
        sp = StringParameter(base=None, value=6.9)
        self.assertEquals(None, sp.get_corresponding_value(6.9))

    def test_sp_set_preset(self):
        """Tests set preset."""
        bp = BaseParameter(
            name="test", corresponding_script=None, preset=False, type=1
        )
        sp = StringParameter(base=bp, value="cookie")

        sp.set_preset("Fluttershy")
        self.assertEquals("Fluttershy", sp.get_value())
        self.assertEquals("Fluttershy", sp.value)
