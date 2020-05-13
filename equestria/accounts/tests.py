import os
import wave
from django.test import TestCase, Client
from django.urls import reverse, resolve
from .views import *
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from accounts.templates import *

# Create your tests here.
"""Module to test upload app."""


class TestAccounts(TestCase):
    """Class to test accounts app."""

    # fixtures = ["equestria/accounts/db.json"]

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

    def test_invalid_login(self):
        """Test logging in with invalid credentials."""
        invalid_credentials = {"username": "testuser", "password": "1337"}
        response = self.client.post(
            "/accounts/login/", invalid_credentials, follow=True
        )
        self.assertFalse(response.context["user"].is_active)
        self.assertEquals(len(response.content), 4437)

    def test_logout(self):
        """Test logout."""
        self.client.post("/accounts/login/", self.credentials, follow=True)
        response = self.client.get(
            "/accounts/logout/", self.credentials, follow=True
        )
        self.assertFalse(response.context["user"].is_active)

    def test_valid_sign_up(self):
        """Test signup with valid credentials."""
        credentials = {"username": "hackerman", "password": "Security1337."}
        get_response = self.client.get("/accounts/signup/")
        self.assertEquals(get_response.status_code, 200)
        # users_before = get_user_model().objects.all().count()
        # print(users_before)
        response = self.client.post(
            "/accounts/signup/", credentials, format="multipart"
        )
        self.assertEquals(response.status_code, 302)
        # User.objects.create_user(**credentials)
        # users = get_user_model().objects.all()
        # print(users)
        # self.assertEqual(users.count(), users_before + 1)

    def test_invalid_sign_up(self):
        """Test signup with invalid credentials."""
        credentials = {"username": "test", "password": "1234"}
        get_response = self.client.get("/accounts/signup/")
        self.assertEquals(get_response.status_code, 200)
        response = self.client.post(
            "/accounts/signup/", credentials, follow=True
        )
        self.assertEquals(len(response.content), 5164)

    def test_forgot_password(self):
        """Test the forgot password page."""
        response = self.client.get("/accounts/forgot/")
        self.assertEquals(response.status_code, 200)
