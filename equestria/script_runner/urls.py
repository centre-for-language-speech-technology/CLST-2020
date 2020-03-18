from django.urls import path
from script_runner.views import *

urlpatterns = [
    path(
<<<<<<< HEAD
        "process/<str:process>/output<path:p>",
        CLAMFetch.as_view(),
        name="clam_fetch",
    ),
    path("process/<int:process_id>", ProcessOverview.as_view(), name="process"),
    path("process/<int:process_id>", ProcessOverview.as_view(), name=""),
=======
        "process/<int:process_id>/<str:process>/output<path:p>",
        CLAMFetch.as_view(),
        name="clam_fetch",
    ),
    path(
        "process/<int:process_id>/", ProcessOverview.as_view(), name="process"
    ),
>>>>>>> 6f7afc8c18d26bd58d9301b5ee0d333edad94638
    path("clam/<path:path>", Downloads.as_view(), name="clam"),
]
