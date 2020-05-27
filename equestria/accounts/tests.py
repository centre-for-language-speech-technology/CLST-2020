from django.test import TestCase
from django.contrib.auth.models import User

# Create your tests here.
"""Module to test upload app."""


class TestAccounts(TestCase):
    """Class to test accounts app."""

    def setUp(self):
        """Set up the data needed to perform tests below."""
        self.credentials = {"username": "testuser", "password": "secret"}
        User.objects.create_user(**self.credentials)

    def test_valid_login(self):
        """Test logging in with valid credentials."""
        get_response = self.client.get("/accounts/login/")
        self.assertEquals(get_response.status_code, 200)
        response = self.client.post(
            "/accounts/login/", self.credentials, follow=True
        )
        self.assertTrue(response.context["user"].is_active)
        self.client.get("/accounts/logout/", self.credentials, follow=True)
        response2 = self.client.get(
            "/accounts/login/?next=/scripts/projects",
            self.credentials,
            format="multipart",
        )
        self.assertEquals(response2.status_code, 200)

    def test_invalid_login(self):
        """Test logging in with invalid credentials."""
        invalid_credentials = {"username": "testuser", "password": "1337"}
        response = self.client.post(
            "/accounts/login/", invalid_credentials, follow=True
        )
        self.assertFalse(response.context["user"].is_active)
        self.assertTrue(b"Invalid username or password" in response.content)

    def test_logout(self):
        """Test logout."""
        self.client.post("/accounts/login/", self.credentials, follow=True)
        response = self.client.get(
            "/accounts/logout/", self.credentials, follow=True
        )
        self.assertFalse(response.context["user"].is_active)
        self.client.post("/accounts/login/", self.credentials, follow=True)
        response = self.client.get(
            "/accounts/logout/?next=/scripts/projects",
            self.credentials,
            format="multipart",
        )
        self.assertFalse(response.context["user"].is_active)
        self.assertEquals(response.status_code, 200)
        response = self.client.get(
            "/accounts/logout/?next=/scripts/projects",
            self.credentials,
            format="multipart",
        )
        self.assertEquals(response.status_code, 302)
        response = self.client.get(
            "/accounts/logout/?next=/", self.credentials, format="multipart"
        )
        self.assertEquals(response.status_code, 302)

    def test_logout_unauthenticated(self):
        """Test unauthenticated user accessing log out with redirect"""
        response = self.client.get(
            "/accounts/logout/?next=/scripts/projects", self.credentials, format="multipart"
        )
        self.assertEquals(response.status_code, 302)

    def test_valid_sign_up(self):
        """Test signup with valid credentials."""
        test_credentials = {
            "username": "test",
            "email": "test@test.com",
            "password1": "75Lh5!@09P%leJYg",
            "password2": "75Lh5!@09P%leJYg",
        }
        test_credentials2 = {
            "username": "test2",
            "email": "test@test.com",
            "password1": "75Lh5!@09P%leJYg",
            "password2": "75Lh5!@09P%leJYg",
        }
        get_response = self.client.get("/accounts/signup/")
        self.assertEquals(get_response.status_code, 200)
        response = self.client.post(
            "/accounts/signup/", test_credentials, format="multipart"
        )
        self.assertEquals(response.status_code, 302)
        self.client.get("/accounts/logout/", self.credentials, follow=True)
        url_with_next = self.client.get(
            "/accounts/signup/?next=/scripts/projects"
        )
        self.assertEquals(get_response.status_code, 200)
        response2 = self.client.post(
            "/accounts/signup/?next=/scripts/projects",
            test_credentials2,
            format="multipart",
        )
        self.assertEquals(response2.status_code, 302)

    def test_invalid_sign_up(self):
        """Test signup with invalid credentials."""
        test_credentials = {"username": "test", "password": "1234"}
        get_response = self.client.get("/accounts/signup/")
        self.assertEquals(get_response.status_code, 200)
        response = self.client.post(
            "/accounts/signup/", test_credentials, follow=True
        )
        self.assertTrue(
            b"Invalid password or already taken user name." in response.content
        )

    def test_forgot_password(self):
        """Test the forgot password page."""
        response = self.client.get("/accounts/forgot/")
        self.assertEquals(response.status_code, 200)
