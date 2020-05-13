from django.contrib import admin
from django.urls import include, path
from equestria.views import *

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", WelcomePage.as_view(), name="welcome"),
    path("upload/", include(("upload.urls", "upload"), namespace="upload")),
    path(
        "scripts/", include(("scripts.urls", "scripts"), namespace="scripts"),
    ),
    path(
        "accounts/",
        include(("accounts.urls", "accounts"), namespace="accounts"),
    ),
]
