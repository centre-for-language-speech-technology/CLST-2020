from rest_framework.generics import (
    RetrieveAPIView,
    ListAPIView,
)
from scripts.models import Profile, Script

from .serializers import (
    ProfileSerializer,
    ScriptSerializer,
    ScriptDetailSerializer,
)


class ScriptListView(ListAPIView):
    """Script API view for listing."""

    serializer_class = ScriptSerializer
    queryset = Script.objects.all()


class ScriptRetrieveView(RetrieveAPIView):
    """Script API view for retrieving."""

    serializer_class = ScriptDetailSerializer
    queryset = Script.objects.all()


class ProfileRetrieveView(RetrieveAPIView):
    """Profile API view for retrieving."""

    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()
