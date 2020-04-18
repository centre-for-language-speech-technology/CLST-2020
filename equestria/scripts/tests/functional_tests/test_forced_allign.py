"""Module to test forced alignment."""
from selenium import webdriver
from django.contrib.staticfiles.testing import StaticLiveServerTestCase


class ForcedAllignmentTest(StaticLiveServerTestCase):
    """Tests related to the forced allignment."""

    def setUp(self):
        """Initialize the webdriver."""
        self.driver = webdriver.Firefox()

    def tearDown(self):
        """Close the driver."""
        self.driver.close()
