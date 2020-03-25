from django.urls import path
from scripts.views import *

urlpatterns = [
    path("fa/", FAView.as_view(), name="fa_create"),
    path(
        "fa/<int:process>",
        ForcedAlignmentProjectDetails.as_view(),
        name="fa_project",
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
    path("", FAView.as_view(), name="forced-alignment"),
]
