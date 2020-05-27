"""Module to parse URL and direct accordingly."""
from django.urls import path, register_converter
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from django.conf import settings
from .views import UploadProjectView, upload_file_view, delete_file_view
from scripts.converters import ProjectConverter

register_converter(ProjectConverter, "project")

urlpatterns = [
    path(
        "<project:project>", UploadProjectView.as_view(), name="upload_project"
    ),
    path("<project:project>/upload", upload_file_view, name="upload_file"),
    path("<project:project>/delete", delete_file_view, name="delete_file"),
]


urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
