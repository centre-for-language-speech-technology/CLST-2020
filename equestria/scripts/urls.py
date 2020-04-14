from django.urls import path
from scripts.views import *

urlpatterns = [
    path("projects", ProjectOverview.as_view(), name="projects"),
    path(
        "fa/status/<int:project_id>", FALoadScreen.as_view(), name="fa_loading",
    ),
    path("fa/<int:project_id>", FAOverview.as_view(), name="fa_overview",),
    path(
        "g2p/status/<int:project_id>",
        G2PLoadScreen.as_view(),
        name="g2p_loading",
    ),
    path(
        "cd/<int:project_id>",
        CheckDictionaryScreen.as_view(),
        name="cd_screen",
    ),
    path(
        "process/<int:process>/status",
        JsonProcess.as_view(),
        name="process_details",
    ),
    path(
        "process/<int:process>/download",
        download_process_archive,
        name="process_download",
    ),
    path(
        "fa/<int:project_id>/start/<int:profile_id>",
        FAStartView.as_view(),
        name="fa_start",
    ),
]
