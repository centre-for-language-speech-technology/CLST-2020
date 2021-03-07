from django.urls import path, include

app_name = "equestria"

urlpatterns = [
    path("projects/", include("projects.api.v1.urls")),
    path("scripts/", include("scripts.api.v1.urls")),
    path("processes/", include("processes.api.v1.urls")),
]
