from django.conf.urls import url
from accounts.views import *

"""Module to parse urls within /accounts/ path."""

urlpatterns = [
    url("signup", Signup.as_view(), name="signup"),
    url("login", Login.as_view(), name="login"),
    url("logout", Logout.as_view(), name="logout"),
    url("settings", Settings.as_view(), name="settings"),
    url("overview", Overview.as_view(), name="overview"),
]
