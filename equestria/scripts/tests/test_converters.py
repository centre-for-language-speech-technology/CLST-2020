from django.test import TestCase
from scripts.converters import ScriptConverter, ProjectConverter, ProfileConverter, ProcessConverter
from scripts.models import Script, Pipeline, InputTemplate, Project, Process, Profile
from unittest.mock import patch

class ConverterTest(TestCase):
    """Tests the script model."""

    fixtures = [
        "projects.json",
    ]

    def setUp(self):
        """Get a script from the db for use in tests."""
        self.dfa = Script.objects.filter(id=1)[0]
        self.p1 = Project.objects.filter(id=1)[0]
        self.pf = Profile.objects.filter(id=1)[0]
        self.ps = Process.objects.filter(id=1)[0]
        
        self.sc = ScriptConverter()
        self.pc = ProjectConverter()
        self.pfc = ProfileConverter()
        self.psc = ProcessConverter()

    def test_s_to_python_good(self):
        """Test if to_python works on good script id"""
        self.assertEquals(self.dfa, self.sc.to_python(1))

    def test_s_to_python_bad(self):
        """Test if to_python works on negative script id"""
        # assert raises doesn't work, I'm sorry for the shit code
        try:
            self.sc.to_python(-1)
        except ValueError:
            self.assertTrue(True)
            return
        self.assertTrue(False)

    def test_s_to_python_bad2(self):
        """Test if to_python works on bad script id"""
        try:
            self.sc.to_python(100)
        except ValueError:
            self.assertTrue(True)
            return
        self.assertTrue(False)


    def test_p_to_python_good(self):
        """Test if to_python works on good script id"""
        self.assertEquals(self.p1, self.pc.to_python(1))

    def test_p_to_python_bad(self):
        """Test if to_python works on negative script id"""
        # assert raises doesn't work, I'm sorry for the shit code
        try:
            self.pc.to_python(-1)
        except ValueError:
            self.assertTrue(True)
            return
        self.assertTrue(False)

    def test_p_to_python_bad2(self):
        """Test if to_python works on bad script id"""
        try:
            self.pc.to_python(100)
        except ValueError:
            self.assertTrue(True)
            return
        self.assertTrue(False)

    def test_pf_to_python_good(self):
        """Test if to_python works on good script id"""
        self.assertEquals(self.pf, self.pfc.to_python(1))

    def test_pf_to_python_bad(self):
        """Test if to_python works on negative script id"""
        # assert raises doesn't work, I'm sorry for the shit code
        try:
            self.pfc.to_python(-1)
        except ValueError:
            self.assertTrue(True)
            return
        self.assertTrue(False)

    def test_pf_to_python_bad2(self):
        """Test if to_python works on bad script id"""
        try:
            self.pfc.to_python(100)
        except ValueError:
            self.assertTrue(True)
            return
        self.assertTrue(False)

    def test_ps_to_python_good(self):
        """Test if to_python works on good script id"""
        self.assertEquals(self.ps, self.psc.to_python(1))

    def test_ps_to_python_bad(self):
        """Test if to_python works on negative script id"""
        # assert raises doesn't work, I'm sorry for the shit code
        try:
            self.psc.to_python(-1)
        except ValueError:
            self.assertTrue(True)
            return
        self.assertTrue(False)

    def test_ps_to_python_bad2(self):
        """Test if to_python works on bad script id"""
        try:
            self.psc.to_python(100)
        except ValueError:
            self.assertTrue(True)
            return
        self.assertTrue(False)

    def test_profile_converter_to_url(self):
        """Test profile converter to_url."""
        self.assertEquals(self.pfc.to_url(self.pf), "1")

    def test_process_converter_to_url(self):
        """Test process converter to_url."""
        self.assertEquals(self.psc.to_url(self.ps), "1")
