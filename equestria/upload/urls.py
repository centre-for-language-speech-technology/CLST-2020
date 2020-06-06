"""Module to parse URL and direct accordingly."""
from django.urls import path, register_converter
from .views import UploadProjectView, delete_file_view
from scripts.converters import ProjectConverter

register_converter(ProjectConverter, "project")

urlpatterns = [
    path(
        "<project:project>", UploadProjectView.as_view(), name="upload_project"
    ),
    path("<project:project>/delete", delete_file_view, name="delete_file"),
]
