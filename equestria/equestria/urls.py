from django.contrib import admin
from django.urls import include, path
from django.contrib.staticfiles.urls import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from equestria.views import *

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", WelcomePage.as_view(), name="welcome"),
    path("praat_scripts/", PraatScripts.as_view(), name="praat_scripts"),
    path(
        "update_dictionary/",
        UpdateDictionary.as_view(),
        name="update_dictionary",
    ),
    path(
        "auto_segmentation/",
        AutoSegmentation.as_view(),
        name="auto_segmentation",
    ),
    path("upload/", include(("upload.urls", "upload"), namespace="upload")),
    path(
        "scripts/", include(("scripts.urls", "scripts"), namespace="scripts"),
    ),
    path(
        "accounts/",
        include(("accounts.urls", "accounts"), namespace="accounts"),
    ),
]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
