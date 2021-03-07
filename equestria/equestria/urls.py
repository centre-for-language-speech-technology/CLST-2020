from django.contrib import admin
from django.urls import include, path
from equestria.views import WelcomePage

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", WelcomePage.as_view(), name="welcome"),
    path(
        "projects/",
        include(("projects.urls", "projects"), namespace="projects"),
    ),
    path(
        "accounts/",
        include(("accounts.urls", "accounts"), namespace="accounts"),
    ),
    path(
        "processes/",
        include(("processes.urls", "processes"), namespace="processes"),
    ),
    path(
        "explainer/",
        include(("explainer.urls", "explainer"), namespace="explainer"),
    ),
    path("api/", include("equestria.api.urls")),
]
