from processes.models import FileSetting, ParameterSetting, Process, LogMessage
from processes.services import get_preferable_files
from rest_framework import serializers
from scripts.models import Script, Profile, InputTemplate, BaseParameter
from processes import models
from projects.api.v1.serializers import FileSerializer


class LogMessageSerializer(serializers.ModelSerializer):
    """Serializer for LogMessage model."""

    class Meta:
        """Meta class."""

        model = LogMessage
        fields = [
            "index",
            "message",
            "time",
        ]


class ProcessSerializer(serializers.ModelSerializer):
    """Serializer for Process model."""

    log_messages = serializers.SerializerMethodField()
    status_string = serializers.SerializerMethodField()
    script_type = serializers.SerializerMethodField()

    def get_log_messages(self, instance):
        """Get the log messages of a Process."""
        return LogMessageSerializer(instance.log_messages, many=True).data

    def get_script_type(self, instance):
        """Get the script type of a Process."""
        return (
            "FA"
            if instance.script == instance.project.pipeline.fa_script
            else "G2P"
        )

    def get_status_string(self, instance):
        """Get the status string of a Process."""
        return instance.get_status_string()

    class Meta:
        """Meta class."""

        model = Process
        fields = [
            "pk",
            "script",
            "script_type",
            "project",
            "status",
            "status_string",
            "log_messages",
            "created",
        ]


class ParameterSerializer(serializers.ModelSerializer):
    """Serializer for Parameter model."""

    value = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    choices = serializers.SerializerMethodField()

    def get_value(self, instance):
        """Get the value of the ParameterSetting belonging to the Parameter."""
        try:
            return ParameterSetting.objects.get(
                base_parameter=instance,
                project=self.context.get("view").kwargs.get("project"),
            ).raw_value
        except ParameterSetting.DoesNotExist:
            return None

    def get_choices(self, instance):
        """Get choices corresponding to Choice parameter."""
        if instance.type == BaseParameter.CHOICE_TYPE:
            return [
                x.value
                for x in instance.get_typed_parameter().get_available_choices()
            ]
        else:
            return None

    def get_type(self, instance):
        """Get the type of a Parameter."""
        if instance.type == BaseParameter.BOOLEAN_TYPE:
            return "Boolean"
        elif instance.type == BaseParameter.STATIC_TYPE:
            return "Static"
        elif instance.type == BaseParameter.STRING_TYPE:
            return "String"
        elif instance.type == BaseParameter.CHOICE_TYPE:
            return "Choice"
        elif instance.type == BaseParameter.TEXT_TYPE:
            return "Text"
        elif instance.type == BaseParameter.INTEGER_TYPE:
            return "Integer"
        else:
            return "Float"

    class Meta:
        """Meta class."""

        model = BaseParameter
        fields = [
            "name",
            "type",
            "value",
            "choices",
        ]


class FileSettingSerializer(serializers.ModelSerializer):
    """Serializer for File model."""

    class Meta:
        """Meta class."""

        model = models.FileSetting
        fields = [
            "file",
        ]


class InputTemplateSettingSerializer(serializers.ModelSerializer):
    """Serializer for input template settings."""

    files = serializers.SerializerMethodField()
    preferable_files = serializers.SerializerMethodField()

    def get_files(self, instance):
        """Get all FileSettings belonging to the InputTemplate."""
        return [
            x.file.id
            for x in FileSetting.objects.filter(
                input_template=instance,
                file__project=self.context.get("view").kwargs.get("project"),
            )
        ]

    def get_preferable_files(self, instance):
        """Get all files preferable for this input template."""
        preferable_files = get_preferable_files(
            self.context.get("view").kwargs.get("project"), instance
        )
        return FileSerializer(preferable_files, many=True).data

    class Meta:
        """Meta class."""

        model = InputTemplate
        fields = [
            "id",
            "template_id",
            "label",
            "unique",
            "optional",
            "files",
            "preferable_files",
        ]


class ProfileSettingSerializer(serializers.ModelSerializer):
    """Serializer for profile settings."""

    input_templates = InputTemplateSettingSerializer(many=True, read_only=False)
    name = serializers.SerializerMethodField()

    def get_name(self, instance):
        """Get name."""
        return instance.__str__()

    class Meta:
        """Meta class."""

        model = Profile
        fields = [
            "id",
            "name",
            "input_templates",
        ]


class SettingsSerializer(serializers.ModelSerializer):
    """Serializer for Product model."""

    profiles = ProfileSettingSerializer(many=True, read_only=False)
    parameters = serializers.SerializerMethodField()

    def get_parameters(self, instance):
        """Get variable parameters."""
        base_parameters = [
            x
            for x in BaseParameter.objects.filter(corresponding_script=instance)
            if not x.preset
        ]
        return ParameterSerializer(
            base_parameters, many=True, read_only=True, context=self.context
        ).data

    class Meta:
        """Meta class."""

        model = Script
        fields = [
            "profiles",
            "parameters",
        ]
