from django.http import HttpResponseNotFound, Http404
from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from os.path import basename, dirname
from django.views.static import serve
from .models import Process, Profile, InputTemplate, Script
from django.http import JsonResponse
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
import secrets
import os
from .forms import ProjectCreateForm
from .tasks import update_script


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


class FAView(LoginRequiredMixin, TemplateView):
    """Class to handle get requests to the forced alignment page."""

    login_url = "/accounts/login/"
    redirect_field_name = "redirect_to"

    template_name = "fa-project-create.html"

    def get(self, request, **kwargs):
        """
        Handle requests to the /forced page.

        Get requests are handled within this class while the upload
        post requests are handled in the upload app
        with callback URLs upload/wav and upload/txt.
        """
        fa_scripts = Script.objects.filter(forced_alignment_script=True)
        form = ProjectCreateForm(None, scripts=fa_scripts)
        fa_projects = Process.objects.filter(script__in=fa_scripts)
        for project in fa_projects:
            project.status_msg = project.get_status()
        return render(
            request,
            self.template_name,
            {"fa_form": form, "processes": fa_projects},
        )

    def post(self, request, **kwargs):
        """
        POST request for the fa-project-create page.

        :param request: the request
        :param kwargs: keyword arguments
        :return: a render of the fa-project-create page
        """
        fa_scripts = Script.objects.filter(forced_alignment_script=True)
        form = ProjectCreateForm(request.POST, scripts=fa_scripts)
        fa_projects = Process.objects.filter(script__in=fa_scripts)
        for project in fa_projects:
            project.status_msg = project.get_status()
        if form.is_valid():
            script_id = form.cleaned_data.get("script")
            project_name = form.cleaned_data.get("project_name")
            fa_script = Script.objects.filter(forced_alignment_script=True).get(
                id=script_id
            )
            process = Process.create_project(project_name, fa_script)
            return redirect("scripts:fa_project", process=process.id)
        return render(
            request,
            self.template_name,
            {"fa_form": form, "processes": fa_projects},
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

    def post(self, request, **kwargs):
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
