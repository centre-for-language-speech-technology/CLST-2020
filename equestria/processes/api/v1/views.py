from django.urls import reverse
from processes.api.v1.serializers import SettingsSerializer, ProcessSerializer
from processes.models import FileSetting, ParameterSetting, Process
from projects.api.v1.permissions import IsOwner
from projects.models import Project
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.exceptions import (
    PermissionDenied,
    MethodNotAllowed,
    ValidationError,
)
from rest_framework.generics import (
    RetrieveUpdateAPIView,
    RetrieveAPIView,
    ListAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from scripts.models import Script, BaseParameter, OutputTemplate
from processes.services import (
    parse_profiles,
    parse_parameters,
    handle_parameter_changing,
    handle_profile_changing,
    autoconfigure_file_settings,
    check_process_ready,
    find_ready_profiles,
)


class ProcessListAPIView(ListAPIView):
    """Process List API View."""

    serializer_class = ProcessSerializer
    owner_key = "user"
    permission_classes = [IsAuthenticated, IsOwner]
    queryset = Process.objects.all()
    ordering = ["created"]

    def get_queryset(self):
        """Get queryset."""
        return self.queryset.filter(project=self.kwargs.get("project"))

    def get_permissions_object(self):
        """Get permissions object."""
        return self.kwargs.get("project")


class ProcessRetrieveAPIView(RetrieveAPIView):
    """Process Retrieve API View."""

    serializer_class = ProcessSerializer
    queryset = Process.objects.all()
    owner_key = "user"
    permission_classes = [IsAuthenticated, IsOwner]

    def get_permissions_object(self):
        """Get permissions object."""
        return Process.objects.get(pk=self.kwargs.get("pk")).project

    def get_queryset(self):
        """Get queryset."""
        return Process.objects.filter(
            project__in=Project.objects.filter(user=self.request.user)
        )


class ScriptSettingsRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    """Script Settings Retrieve Update API View."""

    serializer_class = SettingsSerializer
    queryset = Script.objects.all()
    owner_key = "user"
    permission_classes = [IsAuthenticated, IsOwner]

    def get_permissions_object(self):
        """Get permission object."""
        return self.kwargs.get("project")

    def get_queryset(self):
        """Get queryset."""
        script_list = [
            self.kwargs.get("project").pipeline.fa_script.pk,
            self.kwargs.get("project").pipeline.g2p_script.pk,
        ]
        return self.queryset.filter(pk__in=script_list)

    def update_parameters_and_profiles(self, project, script):
        """Update parameters and profiles."""
        files_altered = []
        parameters_altered = []
        if "profiles" in self.request.data.keys():
            files_altered = handle_profile_changing(
                parse_profiles(self.request.data["profiles"]), project, script
            )
        if "parameters" in self.request.data.keys():
            parameters_altered = handle_parameter_changing(
                parse_parameters(self.request.data["parameters"]),
                project,
                script,
            )
        return files_altered, parameters_altered

    def update(self, request, *args, **kwargs):
        """Update script settings."""
        partial = kwargs.pop("partial", False)
        project = self.kwargs.get("project")
        script = Script.objects.get(pk=self.kwargs.get("pk"))
        if (
            project.pipeline.fa_script == script
            or project.pipeline.g2p_script == script
        ):
            (
                files_altered,
                parameters_altered,
            ) = self.update_parameters_and_profiles(project, script)
            if not partial:
                ParameterSetting.objects.filter(
                    project=project, base_parameter__corresponding_script=script
                ).exclude(pk__in=[x.pk for x in parameters_altered]).delete()
                FileSetting.objects.filter(
                    file__project=project,
                    input_template__corresponding_profile__script=script,
                ).exclude(pk__in=[x.pk for x in files_altered]).delete()
            return self.retrieve(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(["GET", "POST"])
def process_file_list_view(request, **kwargs):
    """List and copy over process output files."""
    process = kwargs.get("process")
    if request.user.is_authenticated and request.user == process.project.user:
        if request.method == "GET":
            return Response(
                status=status.HTTP_200_OK,
                data=[
                    {
                        "file": x,
                        "preset": OutputTemplate.match_any(
                            x, process.script.output_templates
                        ),
                    }
                    for x in process.file_list
                ],
            )
        elif request.method == "POST":
            if (
                "files" in request.data.keys()
                and type(request.data["files"]) == list
            ):
                sanitized_files = [
                    x for x in request.data["files"] if type(x) == str
                ]
                process.move_downloaded_output_files(files=sanitized_files)
                return Response(status=status.HTTP_200_OK)
            else:
                raise ValidationError(
                    detail={"files": "A list of strings is required."}
                )
        else:
            raise MethodNotAllowed(method=request.method)
    else:
        raise PermissionDenied


@api_view(["POST"])
def configure_automatically(request, **kwargs):
    """Configure input templates automatically."""
    project = kwargs.get("project")
    script = kwargs.get("script")
    if request.user.is_authenticated and request.user == project.user:
        if (
            script == project.pipeline.fa_script
            or script == project.pipeline.g2p_script
        ):
            autoconfigure_file_settings(project, script)
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
    else:
        raise PermissionDenied


@api_view(["POST"])
def start_process(request, **kwargs):
    """Start a process."""
    project = kwargs.get("project")
    script = kwargs.get("script")
    profile = kwargs.get("profile", None)
    if request.user.is_authenticated and request.user == project.user:
        if (
            script == project.pipeline.fa_script
            or script == project.pipeline.g2p_script
            and (profile is None or profile.script == script)
        ):
            if profile is None:
                profiles_ready = find_ready_profiles(project, script)
                if len(profiles_ready) == 1:
                    profile = profiles_ready[0]
                elif len(profiles_ready) == 0:
                    return Response(
                        status=status.HTTP_428_PRECONDITION_REQUIRED,
                        data={
                            "errors": [
                                "There is no profile that can be applied to this project, please start a process manually. This can be done on either the Forced Alignment step (for FA processes) or the Grapheen to Phoneem step (for G2P processes)."
                            ]
                        },
                    )

            errors = check_process_ready(project, profile)
            if len(errors) > 0:
                return Response(
                    status=status.HTTP_428_PRECONDITION_REQUIRED,
                    data={"errors": errors},
                )

            process = Process.objects.create(script=script, project=project)
            try:
                process.start_safe(
                    profile,
                    {
                        x.base_parameter.name: x.value
                        for x in ParameterSetting.objects.filter(
                            project=project,
                            base_parameter__corresponding_script=script,
                        )
                    },
                )
            except BaseParameter.ParameterException as e:
                return Response(
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    data={"errors": [e]},
                )
            return Response(
                status=status.HTTP_200_OK,
                data={
                    "errors": [],
                    "process": process.id,
                    "redirect": reverse(
                        "processes:process-detail", kwargs={"process": process},
                    ),
                },
            )
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
    else:
        raise PermissionDenied
