from django.urls import path
from script_runner.views import *

urlpatterns = [
    path("process/<int:process>", ProcessOverview.as_view(), name="process"),
    path(
        "process/<str:process>/output<path:p>",
        CLAMFetch.as_view(),
        name="clam_fetch",
    ),
    path(
        "process/<int:process_id>/", ProcessOverview.as_view(), name="process"
    ),
    path(
        "process/<int:process_id>/status",
        JsonProcess.as_view(),
        name="process_details",
    ),
    path("clam/<path:path>", Downloads.as_view(), name="clam"),
]
