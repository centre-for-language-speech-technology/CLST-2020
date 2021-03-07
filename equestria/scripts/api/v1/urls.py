from django.urls import path
from scripts.api.v1.views import (
    ProfileRetrieveView,
    ScriptListView,
    ScriptRetrieveView,
)

urlpatterns = [
    path(
        "profiles/<int:pk>", ProfileRetrieveView.as_view(), name="profile-list"
    ),
    path("", ScriptListView.as_view(), name="script-list"),
    path("<int:pk>", ScriptRetrieveView.as_view(), name="script-retrieve"),
]
