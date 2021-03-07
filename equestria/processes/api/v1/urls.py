from django.urls import path, register_converter
from processes.api.v1.views import (
    ScriptSettingsRetrieveUpdateAPIView,
    configure_automatically,
    start_process,
    ProcessRetrieveAPIView,
    ProcessListAPIView,
    process_file_list_view,
)
from scripts.converters import ScriptConverter, ProfileConverter
from projects.converters import ProjectConverter


register_converter(ProjectConverter, "project")
register_converter(ScriptConverter, "script")
register_converter(ProfileConverter, "profile")


urlpatterns = [
    path(
        "settings/<project:project>/<int:pk>/",
        ScriptSettingsRetrieveUpdateAPIView.as_view(),
        name="script-settings",
    ),
    path(
        "settings/<project:project>/<script:script>/configure-automatically",
        configure_automatically,
        name="configure-automatically",
    ),
    path(
        "<project:project>/<script:script>/start",
        start_process,
        name="start-process",
    ),
    path(
        "<project:project>/<script:script>/start/<profile:profile>",
        start_process,
        name="start-process",
    ),
    path(
        "details/<int:pk>",
        ProcessRetrieveAPIView.as_view(),
        name="process-retrieve",
    ),
    path(
        "<project:project>", ProcessListAPIView.as_view(), name="process-list",
    ),
    path(
        "<process:process>/files",
        process_file_list_view,
        name="process-files-list",
    ),
]
