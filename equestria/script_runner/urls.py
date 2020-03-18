from django.urls import path
from script_runner.views import *

urlpatterns = [
    path("process/<int:process>", ProcessOverview.as_view(), name="process"),
]
