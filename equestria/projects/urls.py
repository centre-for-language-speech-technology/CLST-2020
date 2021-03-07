"""Module to parse URL and direct accordingly."""
from django.urls import path, register_converter
from .views import *
from .converters import ProjectConverter

register_converter(ProjectConverter, "project")

urlpatterns = [
    path("", ProjectOverview.as_view(), name="overview"),
    path(
        "<project:project>", ProjectDetailView.as_view(), name="project_detail"
    ),
    path(
        "<project:project>/delete",
        ProjectDeleteView.as_view(),
        name="delete_project",
    ),
    path(
        "<project:project>/check-dictionary",
        CheckDictionaryScreen.as_view(),
        name="cd_screen",
    ),
    path("fa/<project:project>", FAOverviewView.as_view(), name="fa_overview",),
]
