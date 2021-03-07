from rest_framework import serializers
from projects import models


class ProjectSerializer(serializers.ModelSerializer):
    """Serializer for Product model."""

    class Meta:
        """Meta class."""

        model = models.Project
        fields = [
            "id",
            "name",
            "pipeline",
        ]


class FileSerializer(serializers.ModelSerializer):
    """Serializer for File model."""

    class Meta:
        """Meta class."""

        model = models.File
        fields = [
            "id",
            "file",
            "filename",
        ]
        read_only_fields = ["filename"]
