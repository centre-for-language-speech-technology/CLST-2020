from django.test import TestCase
from scripts.models import Script, Pipeline
import os
import multiprocessing
from django.core.exceptions import ValidationError

from testing import scallop

GOOD_SERVER = "http://localhost:12345"
BAD_500_SERVER = "http://localhost:12346"


class ScriptModelTest(TestCase):
    """Tests the script model."""

    fixtures = [
        "simple_pipelines.json",
    ]

    #    def scallop(*args):
    #        def _scallop(func):
    #            def wrapper(*args, **kwargs):
    #                scallop = subprocess.Popen(
    #                    ["python3", os.path.join("testing", "scallop.py"), arg]
    #                )
    #                a = func(*args, **kwargs)
    #                scallop.terminate()
    #                return a
    #
    #            return wrapper
    #
    #        if len(args) == 1 and callable(args[0]):
    #            # No arguments, this is the decorator
    #            # Set default values for the arguments
    #            arg = "default"
    #            return _scallop(args[0])
    #        else:
    #            # This is just returning the decorator
    #            arg = args
    #            return _scallop

    @staticmethod
    def _test(msg):
        """Debug method."""
        print(str(msg))
        os.system("dunstify {}".format(str(msg)))

    def setUp(self):
        """Get a script from the db for use in tests."""
        self.dfa = Script.objects.filter(id=1)[0]

    def _setup_scallop(self, method="default"):
        """Legacy."""
        self.p = multiprocessing.Process(target=scallop.start, args=(method,))
        self.p.start()

    def _teardown_scallop(self):
        """Legacy."""
        self.p.terminate()
        self.p.kill()

    def tearDown(self):
        """Run after every test."""
        pass

    def setUpModule(self):
        """Legacy."""
        # _setup_scallop()
        pass

    def tearDownModule(self):
        """Legacy."""
        # _teardown_scallop()
        pass

    def test_number_of_scripts(self):
        """Test if scripts are loaded correctly."""
        self.assertEquals(len(Script.objects.all()), 3)

    def test_name(self):
        """Test if correct script is selected."""
        self.assertEquals(self.dfa.name, "Dutch Forced Alignment")

    def test_server_credentials(self):
        """Test if server credentials are good."""
        self.assertEquals(self.dfa.hostname, GOOD_SERVER)
        self.assertEquals(self.dfa.username, "clst")
        self.assertEquals(self.dfa.password, "clst")

    def test_get_clam_server(self):
        """Test if clam server is defined."""
        self.assertTrue(self.dfa.get_clam_server() is not None)

    #    @scallop
    #    def test_safe_good(self):
    #        self.dfa.save()

    def test_safe_good(self):
        """Test if saving works if the server cooperates."""
        self.dfa.hostname = GOOD_SERVER
        self.dfa.save()

    #    @scallop("error")
    def test_safe_fail(self):
        """Test that saving does not work if the server is faulty."""
        self.dfa.hostname = BAD_500_SERVER
        # self.assertRaises(ValidationError, self.dfa.save())
        # does not work for some reason
        raises_validation_error = False
        try:
            self.dfa.save()
            self.dfa.refresh()
        except ValidationError:
            raises_validation_error = True
        self.assertTrue(raises_validation_error)

    def test_pipeline_good(self):
        name = "test_pipeline"
        self.pipeline = Pipeline.objects.create(
            name = "test_pipeline",
            fa_script = self.dfa,
            g2p_script = self.dfa,
        )
        self.assertEquals(self.pipeline.__str__(), name)
        self.assertEquals(self.pipeline.fa_script, self.dfa)

    def test_input_template(self):
        pass
