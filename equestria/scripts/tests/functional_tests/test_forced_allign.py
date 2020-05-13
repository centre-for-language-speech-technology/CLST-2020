"""Module to test forced alignment."""
from equestria.tests.functional_tests.meta import GenericFuncTest
import time


class ForcedAllignmentTest(GenericFuncTest):
    pass


class TestUI(GenericFuncTest):
    """Tests basic UI elements."""

    fixtures = ["simple_pipelines"]

    def test_welcome_test(self):
        """Test if user is greeted by welcome text."""
        self.get_page()
        text = self.get("/html/body/div/div/h1")
        subtext = self.get("/html/body/div/div/h4")
        self.assertEquals(text.text, "Equestria")
        self.assertEquals(
            subtext.text,
            "A Forced Alignment Pipeline",
        )
