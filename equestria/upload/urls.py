"""Module to parse URL and direct accordingly."""
from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from django.conf import settings
from .views import UploadProjectView

urlpatterns = [
    path(
        "<int:project_id>", UploadProjectView.as_view(), name="upload_project"
    ),
]


urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
