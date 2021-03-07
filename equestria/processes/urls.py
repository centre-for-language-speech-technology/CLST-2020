from django.urls import register_converter, path
from .views import (
    ProcessDetailView,
    FAProcessOverviewView,
    G2PProcessOverviewView,
)
from .converters import ProcessConverter
from projects.converters import ProjectConverter


register_converter(ProcessConverter, "process")
register_converter(ProjectConverter, "project")

urlpatterns = [
    path(
        "<process:process>", ProcessDetailView.as_view(), name="process-detail",
    ),
    path(
        "project/<project:project>/fa",
        FAProcessOverviewView.as_view(),
        name="fa-process-overview",
    ),
    path(
        "project/<project:project>/g2p",
        G2PProcessOverviewView.as_view(),
        name="g2p-process-overview",
    ),
]
