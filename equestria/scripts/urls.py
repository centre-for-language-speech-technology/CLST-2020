"""Module to parse URL and direct accordingly."""
from django.urls import path, register_converter
from .views import *
from .converters import ProjectConverter, ProfileConverter, ProcessConverter

register_converter(ProjectConverter, "project")
register_converter(ProfileConverter, "profile")
register_converter(ProcessConverter, "process")

urlpatterns = [
    path("projects", ProjectOverview.as_view(), name="projects"),
    path(
        "fa/status/<project:project>",
        FALoadScreen.as_view(),
        name="fa_loading",
    ),
    path(
        "redirect/<project:project>", FARedirect.as_view(), name="fa_redirect",
    ),
    path("fa/<project:project>", FAOverview.as_view(), name="fa_overview",),
    path(
        "g2p/status/<project:project>",
        G2PLoadScreen.as_view(),
        name="g2p_loading",
    ),
    path(
        "cd/<project:project>",
        CheckDictionaryScreen.as_view(),
        name="cd_screen",
    ),
    path(
        "process/<process:process>/status",
        JsonProcess.as_view(),
        name="process_details",
    ),
    path(
        "project/<project:project>/download",
        download_project_archive,
        name="project_download",
    ),
    path(
        "fa/<project:project>/start/<profile:profile>",
        FAStartView.as_view(),
        name="fa_start",
    ),
    path(
        "g2p/<project:project>/start/<profile:profile>",
        G2PStartScreen.as_view(),
        name="g2p_start",
    ),
]
