from django.conf.urls import url
from accounts.views import *

urlpatterns = [
    url(r"^signup/$", Signup.as_view(), name="signup"),
    url(r"^login/$", Login.as_view(), name="login"),
    url(r"^logout/$", Logout.as_view(), name="logout"),
]
