from selenium import webdriver
from django.contrib.staticfiles.testing import StaticLiveServerTestCase


class GenericFuncTest(StaticLiveServerTestCase):
    """Tests related to the sidebar."""

    def setUp(self):
        """Initialize the webdriver."""
        self.driver = webdriver.Firefox()

    def tearDown(self):
        """Close the driver."""
        self.driver.close()

    def get_page(self):
        """Open the live server page."""
        self.driver.get(self.live_server_url)

    def get(self, xpath):
        """
        Return an element specified by xpath.

        :param xpath: xpath selector for element
        :return: element if it exists
        """
        return self.driver.find_element_by_xpath(xpath)

    def get_id(self, id):
        """
        Return an element by specified by id.

        :param id: id selector for element
        :return: element if it exists
        """
        return self.driver.find_element_by_id(id)

    def _has_class(self, element, class_name):
        """
        Return if an element has a class.

        :param element: element to check
        :param class_name: class name element should have
        """
        return class_name in element.get_attribute("class").split()

    def has_class(self, element, class_name):
        """
        Check if element has a class with name class_name.

        :param element: element to check
        :param class_name: class name element should have
        """
        self.assertTrue(self._has_class(element, class_name))

    def not_has_class(self, element, class_name):
        """
        Check if element doesn't have a class with name class_name.

        :param element: element to check
        :param class_name: class name element should have
        """
        self.assertFalse(self._has_class(element, class_name))


class TestUI(GenericFuncTest):
    """Tests basic UI elements."""

    def test_welcome_test(self):
        """Test if user is greeted by welcome text."""
        self.get_page()
        text = self.get("/html/body/div[2]/h1")
        subtext = self.get("/html/body/div[2]/h4")
        self.assertEquals(text.text, "Welcome to Equestria!")
        self.assertEquals(
            subtext.text,
            "With this tool you will be able to perform forced alignment and analyse the result using Praat scripts.",
        )

    def test_page_goes_dark_when_sidebar_is_opened(self):
        """Test if the page goes dark when the sidebar is open."""
        self.get_page()
        hamburger_button = self.get("/html/body/div[1]/div[3]/button")
        dark_overlay = self.get_id("overlay")
        self.has_class(hamburger_button, "is-closed")
        self.not_has_class(dark_overlay, "overlay")
        hamburger_button.click()
        self.has_class(hamburger_button, "is-open")
        self.has_class(dark_overlay, "overlay")
