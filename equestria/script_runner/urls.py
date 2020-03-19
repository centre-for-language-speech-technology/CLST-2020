from django.urls import path
from script_runner.views import *

urlpatterns = [
    path("d/<path:path>", Downloads.as_view(), name="downloads"),
    path("process/<int:process>", ProcessOverview.as_view(), name="process"),
]
