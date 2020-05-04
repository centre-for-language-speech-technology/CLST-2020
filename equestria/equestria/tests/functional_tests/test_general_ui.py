from equestria.tests.functional_tests.meta import GenericFuncTest


class TestUI(GenericFuncTest):
    """Tests basic UI elements."""

    def test_welcome_test(self):
        """Test if user is greeted by welcome text."""
        self.get_page()
        text = self.get("/html/body/div/h1")
        subtext = self.get("/html/body/div/h4")
        self.assertEquals(text.text, "Welcome to Equestria!")
        self.assertEquals(
            subtext.text,
            "With this tool you will be able to perform forced alignment and analyse the result using Praat scripts.",
        )
