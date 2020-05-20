from django.test import TestCase
from scripts.models import Profile, Process, Script, InputTemplate
from equestria.settings.base import BASE_DIR
import os


class TestProfile(TestCase):
    """Test the Profile model"""

    fixtures = [
        "simple_pipelines.json",
    ]

    def setUp(self):
        """Set up the data needed to perform tests below."""
        self.profile1 = Profile.objects.create(script=Script.objects.all()[0])
        self.input_template1 = InputTemplate.objects.create(
            template_id="Profile",
            format="<class 'clam.common.data.PlainTextFormat'>",
            label="Profile Input Template",
            mime="text/plain",
            extension="txt",
            optional=False,
            unique=True,
            accept_archive=False,
            corresponding_profile=self.profile1,
        )

    def test_profile_exists(self):
        """Test if profile has been added to database"""
        profile_exists = self.profile1 in Profile.objects.all()
        self.assertTrue(profile_exists)

    def test_str(self):
        """Test if string conversion method gives a string of the id of the project"""
        string = str(self.profile1)
        self.assertEquals(string, str(self.profile1.id))

    def test_remove_corresponding_templates(self):
        """Test if the corresponding templates gets removed properly"""
        input_templates_before = InputTemplate.objects.filter(
            corresponding_profile=self.profile1
        )
        self.assertTrue(self.input_template1 in input_templates_before)
        self.profile1.remove_corresponding_templates()
        input_templates = InputTemplate.objects.filter(
            corresponding_profile=self.profile1
        )
        self.assertFalse(self.input_template1 in input_templates)

    def test_invalid_profile(self):
        """Test if invalid profile is seen as invalid"""
        folder = os.path.abspath(os.path.dirname(__file__))
        self.assertFalse(self.profile1.is_valid(folder))

    def test_valid_profile(self):
        """Test if valid profile is seen as valid"""
        profile2 = Profile.objects.create(script=Script.objects.all()[1])
        folder = os.path.abspath(os.path.dirname(__file__))
        folder2 = os.path.join(BASE_DIR, "test-files")
        self.assertTrue(profile2.is_valid(folder))
        self.assertTrue(self.profile1.is_valid(folder2))

    def test_get_valid_files(self):
        """Test if get_valid_files() returns the correct list of valid files in the folder"""
        folder1 = os.path.abspath(os.path.dirname(__file__))
        self.assertEquals(self.profile1.get_valid_files(folder1), {1: []})
        folder2 = os.path.join(BASE_DIR, "test-files")
        self.assertEquals(
            self.profile1.get_valid_files(folder2), {1: ["test.txt"]}
        )
