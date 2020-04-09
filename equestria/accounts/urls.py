from django.conf.urls import url
from accounts.views import *

"""Module to parse urls within /accounts/ path."""

urlpatterns = [
    url(r"^signup/$", Signup.as_view(), name="signup"),
    url(r"^login/$", Login.as_view(), name="login"),
    url(r"^logout/$", Logout.as_view(), name="logout"),
    url(r"^settings/$", Settings.as_view(), name="settings"),
    url(r"^overview/$", Overview.as_view(), name="overview"),
]
