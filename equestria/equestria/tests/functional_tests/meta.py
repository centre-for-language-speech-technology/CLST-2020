from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
import shutil
import os


class GenericFuncTest(StaticLiveServerTestCase):
    """Tests related to the sidebar."""

    def setUp(self):
        """Initialize the webdriver."""
        self.driver = webdriver.Firefox()
        # Wait up to 100s before failing to access element
        self.driver.implicitly_wait(100)
        try:
            shutil.rmtree(os.path.join("equestria", "userdata", "testuser"))
        except:
            pass

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

    def login_and_go_to_start(self):
        """
        Sign in as new user and go to home screen.
        """
        self.get_page()
        # Click start adventure button
        self.get('//*[@id="inputGroupFileAddon02"]').click()
        self.assertTrue(
            self.driver.current_url.endswith(
                "/accounts/login/?next=/scripts/projects"
            )
        )
        # Click on signup link
        self.get("/html/body/div/div/div/a[1]").click()
        self.get_id("id_username").send_keys("testuser")
        self.get_id("id_password1").send_keys("X07@!nhubY8agly9")
        self.get_id("id_password2").send_keys("X07@!nhubY8agly9")
        # Confirm Signup button
        self.get("/html/body/div/div/form/input[5]").click()
        self.assertEqual(self.driver.current_url, self.live_server_url + "/")
