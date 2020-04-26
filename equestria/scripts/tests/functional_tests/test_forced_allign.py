"""Module to test forced alignment."""
from equestria.tests.functional_tests.meta import GenericFuncTest
import time


class ForcedAllignmentTest(GenericFuncTest):
    pass


class TestUI(GenericFuncTest):
    """Tests basic UI elements."""
    fixtures = ['simple_pipelines']

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

    def test_create_project(self):
        """Test if creating a project displays that project."""
        self.login_and_go_to_start()
        # Click start adventure button
        self.get('//*[@id="inputGroupFileAddon02"]').click()
        self.get_id("id_project_name").send_keys("testproject")
        # Click create button
        self.get("/html/body/div[1]/div/form/div/input[2]").click()
        print(self.driver.current_url)
        self.assertTrue("upload/" in self.driver.current_url)
        # Click on Select Project button in navbar to go a step back
        self.get("/html/body/nav[2]/ul/li[1]/a").click()
        new_project_on_page = False
        for h4 in self.driver.find_elements_by_tag_name('h4'):
            new_project_on_page = new_project_on_page or "Name: testproject" == h4.text
        self.assertTrue(new_project_on_page)

            
        
