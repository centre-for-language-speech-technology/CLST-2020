from rest_framework import serializers
from scripts import models


class ParameterSerializer(serializers.ModelSerializer):
    """Serializer for Parameter model."""

    class Meta:
        """Meta class."""

        model = models.BaseParameter
        fields = [
            "name",
            "corresponding_script",
            "preset",
            "type",
            "value",
        ]


class InputTemplateSerializer(serializers.ModelSerializer):
    """Serializer for InputTemplate model."""

    class Meta:
        """Meta class."""

        model = models.InputTemplate
        fields = [
            "id",
            "template_id",
            "format",
            "label",
            "mime",
            "extension",
            "optional",
            "unique",
            "accept_archive",
        ]


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for Product model."""

    input_templates = InputTemplateSerializer(many=True, read_only=True)
    name = serializers.SerializerMethodField()

    def get_name(self, instance):
        """Get name."""
        return instance.__str__()

    class Meta:
        """Meta class."""

        model = models.Profile
        fields = [
            "id",
            "name",
            "script",
            "input_templates",
        ]


class ScriptDetailSerializer(serializers.ModelSerializer):
    """Serializer for Script model."""

    profiles = ProfileSerializer(many=True, read_only=True)
    parameters = ParameterSerializer(many=True, read_only=True)

    class Meta:
        """Meta class."""

        model = models.Script
        fields = [
            "name",
            "description",
            "profiles",
            "parameters",
        ]


class ScriptSerializer(serializers.ModelSerializer):
    """Serializer for Script model."""

    class Meta:
        """Meta class."""

        model = models.Script
        fields = [
            "id",
            "name",
            "description",
        ]
