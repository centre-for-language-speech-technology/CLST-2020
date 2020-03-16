from django.urls import path
from script_runner.views import *

urlpatterns = [
    path("d/<path:path>", Downloads.as_view(), name="downloads"),
    path("<str:output_file>", Outputs.as_view(), name="outputs"),
]
