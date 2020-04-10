from django.http import HttpResponseNotFound, Http404
from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from os.path import basename, dirname
from django.views.static import serve
from .models import Project, Profile, InputTemplate, Script, Pipeline, Process
from django.http import JsonResponse
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
import secrets
import os
from .forms import ProjectCreateForm
from .tasks import update_script


class FAStartView(LoginRequiredMixin, TemplateView):
    """Start view for Forced Alignment."""

    login_url = "/accounts/login/"

    def post(self, request, **kwargs):
        """
        Post method for start view.

        :param request: the request
        :param kwargs: the keyword arguments
        :return: a JSON response indicating whether the CLAM server started
        """
        project_id = kwargs.get("project_id")
        try:
            project = Project.objects.filter(user=request.user.id).get(
                id=project_id
            )
        except Project.DoesNotExist:
            return JsonResponse(
                {"status": "error", "error": "Project does not exist"}
            )
        if project.current_process is None:
            project.current_process = Process.create_process(
                project.pipeline.fa_script
            )
            project.save()
            project.current_process.remove_corresponding_profiles()
            project.delete()
            return JsonResponse({"status": "succes"})
        else:
            return JsonResponse(
                {
                    "status": "error",
                    "error": "There is already a running process for this project",
                }
            )


class FALoadScreen(LoginRequiredMixin, TemplateView):
    """
    Loading indicator for Forced Alignment.

    This class shows the loading status to the user
    If needed, it launches a new process. If the user refreshes this page
    and a FA script is already running, it wont start a new process.
    """

    login_url = "/accounts/login/"

    template_name = "fa-loadingscreen.html"

    def get(self, request, **kwargs):
        """
        GET request for loading page.

        :param request: the request
        :param kwargs: keyword arguments
        :return: a render of the fa loading screen
        """
        return render(request, self.template_name, {},)


class FAOverview(LoginRequiredMixin, TemplateView):
    """After the script is done, this screen shows the results."""

    login_url = "/accounts/login/"

    template_name = "fa-overviewpage.html"

    def get(self, request, **kwargs):
        """
        GET request for FA overview page.

        :param request: the request
        :param kwargs: keyword arguments
        :return: a render of the FA overview page
        """
        return render(request, self.template_name, {},)


class G2PLoadScreen(LoginRequiredMixin, TemplateView):
    """Loading screen, where the g2p is run as well."""

    login_url = "/accounts/login/"

    template_name = "g2p-loadingscreen.html"

    def get(self, request, **kwargs):
        """
        GET request for G2P loading screen.

        :param request: the request
        :param kwargs: keyword arguments
        :return: a render of the G2P loading screen
        """
        return render(request, self.template_name, {},)


class CheckDictionaryScreen(LoginRequiredMixin, TemplateView):
    """Check dictionary page."""

    login_url = "/accounts/login/"

    template_name = "check-dictionary-screen.html"

    def get(self, request, **kwargs):
        """
        GET request for the check dictionary page.

        :param request: the request
        :param kwargs: keyword arguments
        :return: a render of the check dictionary page
        """
        return render(request, self.template_name, {},)


class JsonProcess(TemplateView):
    """View for representing Processes as JSON."""

    def get(self, request, **kwargs):
        """
        Get request, actually redirecting everything to the POST method.

        :param request: the request of the user
        :param kwargs: the keyword arguments
        :return: the same as self.post returns
        """
        return self.post(request, **kwargs)

    def post(self, request, **kwargs):
        """
        Post request, used for serving AJAX requests the information they need.

        :param request: the request of the user
        :param kwargs: the keyword arguments
        :return: a JsonResponse containing the following information:
                    - status (of the process)
                    - status_message
                    - errors (true or false, if errors occurred)
                    - error_message (emtpy if no errors occurred, a message otherwise)
        """
        key = kwargs.get("process")
        process = Process.objects.get(pk=key)
        clam_status = process.get_status()
        clam_msg = process.get_status_messages()
        log_messages = JsonProcess.construct_clam_log_format(clam_msg)
        return JsonResponse({"status": clam_status, "log": log_messages})

    @staticmethod
    def construct_clam_log_format(clam_msg):
        """
        Construct a JSON compatible format for CLAM log messages.

        :param clam_msg: a list of LogMessage objects
        :return: a list of dictionaries, each containing a 'time' and 'message' key with the time and message of the
        LogMessage object
        """
        log_messages = []
        for item in clam_msg:
            log_messages.append(
                {"time": item.time.__str__(), "message": item.message}
            )
        return log_messages


class ProjectOverview(LoginRequiredMixin, TemplateView):
    """Class to handle get requests to the project overview page."""

    login_url = "/accounts/login/"

    template_name = "project-overview.html"

    def get(self, request, **kwargs):
        """
        Handle requests to the project create page.

        Get requests are handled within this class while the upload
        post requests are handled in the upload app
        with callback URLs upload/wav and upload/txt.
        """
        pipelines = Pipeline.objects.all()
        form = ProjectCreateForm(request.user, None, pipelines=pipelines)
        projects = Project.objects.filter(user=request.user.id)
        return render(
            request, self.template_name, {"form": form, "projects": projects},
        )

    def post(self, request, **kwargs):
        """
        POST request for the project create page.

        :param request: the request
        :param kwargs: keyword arguments
        :return: a render of the fa-project-create page
        """
        pipelines = Pipeline.objects.all()
        form = ProjectCreateForm(
            request.user, request.POST, pipelines=pipelines
        )
        projects = Project.objects.filter(user=request.user.id)
        if form.is_valid():
            pipeline_id = form.cleaned_data.get("pipeline")
            project_name = form.cleaned_data.get("project_name")
            pipeline = Pipeline.objects.get(id=pipeline_id)
            process = Process.create_process(pipeline.fa_script)

            project = Project.create_project(
                project_name, pipeline, request.user
            )
            project.current_process = process
            project.save()
            return redirect("upload:upload_project", project_id=project.id)
        return render(
            request, self.template_name, {"form": form, "projects": projects},
        )


class ForcedAlignmentProjectDetails(TemplateView):
    """Project overview page."""

    template_name = "fa-project-details.html"

    def get(self, request, **kwargs):
        """
        GET request for project overview page.

        :param request: the request
        :param kwargs: keyword arguments
        :return: A render of 404 or fa-project-details page
        """
        process = Process.objects.get(id=kwargs.get("process"))
        if process is not None:
            profiles = Profile.objects.filter(process=process)
            for profile in profiles:
                profile.input_templates = InputTemplate.objects.select_related().filter(
                    corresponding_profile=profile.id
                )
            return render(
                request,
                self.template_name,
                {"profiles": profiles, "process": process},
            )
        else:
            raise Http404("Project not found")

    def post(self, request, *args, **kwargs):
        """
        POST request for project overview page.

        :param request: the request
        :param kwargs: keyword arguments
        :return: A 404 or redirecto to the fa_project page
        """
        profile_id = request.POST.get("profile_id", None)
        if profile_id is None:
            raise Http404("Bad request")

        profile = Profile.objects.get(pk=profile_id)

        if ForcedAlignmentProjectDetails.run_profile(profile, request.FILES):
            return redirect("scripts:fa_project", process=profile.process.id)
        else:
            raise Http404("Something went wrong with processing the files.")

    @staticmethod
    def run_profile(profile, files):
        """
        Run a specified process with the given profile.

        :param profile: the profile to run
        :param files: the files to be uploaded to the CLAM server
        :return: None
        """
        argument_files = list()
        for input_template in InputTemplate.objects.select_related().filter(
            corresponding_profile=profile
        ):
            random_token = secrets.token_hex(32)
            file_name = os.path.join(settings.TMP_DIR, random_token)
            with open(file_name, "wb",) as file:
                for chunk in files[str(input_template.id)]:
                    file.write(chunk)
            argument_files.append((file_name, input_template.template_id,))
        profile.process.start(argument_files)
        update_script(profile.process.id)
        return True


def download_process_archive(request, **kwargs):
    """Download the archive containing the process files."""
    process = Process.objects.get(pk=kwargs.get("process"))
    if process.output_file is not None:
        return serve(
            request, basename(process.output_file), dirname(process.output_file)
        )
    else:
        return HttpResponseNotFound("Downloaded archive not found")
