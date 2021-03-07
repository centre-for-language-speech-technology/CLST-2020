from django.urls import path, register_converter
from projects.api.v1.views import (
    ProjectListCreateView,
    FileListCreateView,
    FileRetrieveDestroyView,
    ProjectRetrieveDestroyView,
    project_clear_files,
    download_project_file,
    dictionary_get_update,
    download_project_archive,
)
from projects.converters import ProjectConverter


register_converter(ProjectConverter, "project")

urlpatterns = [
    path("", ProjectListCreateView.as_view(), name="project-listcreate"),
    path(
        "<int:pk>/",
        ProjectRetrieveDestroyView.as_view(),
        name="project-retrievedestroy",
    ),
    path(
        "<project:project>/files/",
        FileListCreateView.as_view(),
        name="project-file-listcreate",
    ),
    path(
        "<project:project>/files/<int:pk>/",
        FileRetrieveDestroyView.as_view(),
        name="project-file-retrievedestroy",
    ),
    path(
        "<project:project>/files/clear/",
        project_clear_files,
        name="project-file-clear",
    ),
    path(
        "<project:project>/files/<int:pk>/download/",
        download_project_file,
        name="project-file-download",
    ),
    path(
        "<project:project>/files/download/",
        download_project_archive,
        name="project-archive-download",
    ),
    path(
        "<project:project>/dictionary",
        dictionary_get_update,
        name="dictionary-get-update",
    ),
]
