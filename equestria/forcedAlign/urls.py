from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from django.conf import settings
from .views import FAView, ForcedAlignmentProjectDetails

urlpatterns = [
    path("", FAView.as_view(), name="FA_form"),
    path("<str:project>", ForcedAlignmentProjectDetails.as_view(), name="fa_project")
]


urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
