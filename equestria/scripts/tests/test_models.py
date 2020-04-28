from django.test import TestCase
from scripts.models import Script
import os


class ScriptModelTest(TestCase):
    """Tests the script model."""

    fixtures = [
        "simple_pipelines.json",
    ]

    @staticmethod
    def _test(msg):
        print(str(msg))
        os.system("dunstify {}".format(str(msg)))

    def setUp(self):
        self.dfa = Script.objects.filter(id=1)[0]

    def test_number_of_scripts(self):
        self.assertEquals(len(Script.objects.all()), 3)

    def test_name(self):
        self.assertEquals(self.dfa.name, "Dutch Forced Alignment")

    def test_server_credentials(self):
        self.assertEquals(self.dfa.hostname, "http://localhost:12345")
        self.assertEquals(self.dfa.username, "clst")
        self.assertEquals(self.dfa.password, "clst")

    def test_get_clam_server(self):
        self.assertTrue(self.dfa.get_clam_server() is not None)

    def test_safe(self):
        self.dfa.save()
