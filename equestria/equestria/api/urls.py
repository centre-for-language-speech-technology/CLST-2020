from django.urls import path, include

urlpatterns = [
    path(
        "",
        include(
            [path("v1/", include("equestria.api.v1.urls", namespace="v1")),]
        ),
    )
]
