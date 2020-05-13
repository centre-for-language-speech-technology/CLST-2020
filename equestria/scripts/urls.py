"""Module to parse URL and direct accordingly."""
from django.urls import path, register_converter
from .views import *
from .converters import (
    ProjectConverter,
    ProfileConverter,
    ProcessConverter,
    ScriptConverter,
)

register_converter(ProjectConverter, "project")
register_converter(ProfileConverter, "profile")
register_converter(ProcessConverter, "process")
register_converter(ScriptConverter, "script")

urlpatterns = [
    path("projects", ProjectOverview.as_view(), name="projects"),
    path(
        "projects/<project:project>/delete",
        ProjectDeleteView.as_view(),
        name="delete_project",
    ),
    path(
        "redirect/<project:project>", FARedirect.as_view(), name="fa_redirect",
    ),
    path("fa/<project:project>", FAOverview.as_view(), name="fa_overview",),
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
        "<project:project>/autostart/<script:script>",
        AutomaticScriptStartView.as_view(),
        name="start_automatic",
    ),
    path(
        "<project:project>/start/<script:script>/<profile:profile>",
        ScriptStartView.as_view(),
        name="start",
    ),
    path(
        "<project:project>/status/<script:script>",
        ScriptLoadScreen.as_view(),
        name="loading",
    ),
]
