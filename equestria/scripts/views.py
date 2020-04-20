"""Module to handle uploading files."""
from django.http import Http404
from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from os.path import basename, dirname
from django.views.static import serve
from .models import (
    Project,
    Profile,
    Pipeline,
    Process,
    STATUS_FINISHED,
)
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import ProjectCreateForm, AlterDictionaryForm
from .tasks import update_script
import logging


class FARedirect(LoginRequiredMixin, TemplateView):
    """Start view for Forced Alignment."""

    login_url = "/accounts/login/"

    template_name = ""

    def get(self, request, **kwargs):
        """
        GET method for the redirecting. This only redirects.

        :param request: the request
        :param kwargs: the keyword arguments
        :return: a redirect to another page, a 404 if the project does not exist and a nice state error if some
        things fail.
        """
        project_id = kwargs.get("project_id")

        try:
            project = Project.objects.filter(user=request.user.id).get(
                id=project_id
            )
        except Project.DoesNotExist:
            raise Http404("Project does not exist")

        if (
            project.current_process.script == project.pipeline.fa_script
            and project.current_process.status == STATUS_FINISHED
        ):
            if project.has_non_empty_extension_file([".oov"]):
                # TODO: maybe remove the old process here?
                g2p_process = Process.create_process(
                    project.pipeline.g2p_script, project.folder
                )
                try:
                    profile = Profile.objects.get(process=g2p_process)
                except Profile.MultipleObjectsReturned:
                    # TODO: Make a nice error screen
                    g2p_process.remove_corresponding_profiles()
                    g2p_process.delete()
                    raise Profile.MultipleObjectsReturned
                project.current_process = g2p_process
                project.save()
                return redirect(
                    "scripts:g2p_start",
                    project_id=project_id,
                    profile_id=profile,
                )
            else:
                return redirect("scripts:cd_screen", project_id=project_id)
        elif project.current_process.script == project.pipeline.g2p_script:
            try:
                profile = Profile.objects.get(process=project.current_process)
            except Profile.MultipleObjectsReturned:
                # TODO: Make a nice error screen
                raise Profile.MultipleObjectsReturned
            return redirect(
                "scripts:g2p_start", project_id=project_id, profile_id=profile
            )
        else:
            raise Project.StateException


class FAStartView(LoginRequiredMixin, TemplateView):
    """Start view for Forced Alignment."""

    login_url = "/accounts/login/"

    template_name = "fa-start.html"

    def get(self, request, **kwargs):
        """
        GET method for start view.

        :param request: the request
        :param kwargs: the keyword arguments
        :return: a JSON response indicating whether the CLAM server started
        """
        project_id = kwargs.get("project_id")
        profile_id = kwargs.get("profile_id")
        try:
            project = Project.objects.filter(user=request.user.id).get(
                id=project_id
            )
            profile = Profile.objects.get(id=profile_id)
        except Project.DoesNotExist or Profile.DoesNotExist:
            return render(
                request,
                self.template_name,
                {
                    "project": project_id,
                    "error": "Either the profile or project does not exist",
                },
            )
        process = project.current_process
        if process.script != project.pipeline.fa_script:
            return render(
                request,
                self.template_name,
                {
                    "project": project_id,
                    "error": "Current process is not a Forced Alignment process",
                },
            )
        if profile.process != process:
            return render(
                request,
                self.template_name,
                {
                    "project": project_id,
                    "error": "Invalid profile for the specified process",
                },
            )

        try:
            process.start_safe(profile)
        except ValueError as e:
            logging.error(e)
            return render(
                request,
                self.template_name,
                {
                    "project": project_id,
                    "error": "Error while starting the process, make sure all input"
                    " files are specified",
                },
            )
        except Exception as e:
            logging.error(e)
            return render(
                request,
                self.template_name,
                {
                    "project": project_id,
                    "error": "Error while uploading files to CLAM, please try again later",
                },
            )
        update_script(process.id)
        return redirect("scripts:fa_loading", project_id=project_id)


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
        project_id = kwargs.get("project_id")
        try:
            project = Project.objects.filter(user=request.user.id).get(
                id=project_id
            )
        except Project.DoesNotExist:
            return Http404("Project does not exist")

        if project.current_process.script != project.pipeline.fa_script:
            raise Project.StateException(
                "Current project script is no forced alignment script"
            )

        return render(
            request,
            self.template_name,
            {"process": project.current_process, "project": project},
        )


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
        project_id = kwargs.get("project_id")
        try:
            project = Project.objects.filter(user=request.user.id).get(
                id=project_id
            )
        except Project.DoesNotExist:
            return Http404("Project does not exist")

        if project.finished_fa():
            return render(
                request,
                self.template_name,
                {"success": True, "project_id": project.id},
            )
        else:
            return render(
                request,
                self.template_name,
                {"success": False, "project_id": project.id},
            )


class G2PStartScreen(LoginRequiredMixin, TemplateView):
    """Start screen of the g2p."""

    login_url = "/accounts/login/"

    template_name = "g2p-startscreen.html"

    def get(self, request, **kwargs):
        """
        GET method for the start screen of G2P.

        :param request: the request
        :param kwargs: the keyword arguments
        :return: a JSON response indicating whether the CLAM server started
        """
        project_id = kwargs.get("project_id")
        profile_id = kwargs.get("profile_id")
        try:
            project = Project.objects.filter(user=request.user.id).get(
                id=project_id
            )
            profile = Profile.objects.get(id=profile_id)
        except Project.DoesNotExist or Profile.DoesNotExist:
            return render(
                request,
                self.template_name,
                {
                    "project": project_id,
                    "error": "Either the profile or project does not exist",
                },
            )
        process = project.current_process
        if process.script != project.pipeline.g2p_script:
            print(process.script)
            return render(
                request,
                self.template_name,
                {
                    "project": project_id,
                    "error": "Current process is not a G2P process",
                },
            )
        if profile.process != process:
            return render(
                request,
                self.template_name,
                {
                    "project": project_id,
                    "error": "Invalid profile for the specified process",
                },
            )

        try:
            process.start_safe(profile)
        except ValueError as e:
            logging.error(e)
            return render(
                request,
                self.template_name,
                {
                    "project": project_id,
                    "error": "Error while starting the process, make sure all input"
                    " files are specified",
                },
            )
        except Exception as e:
            logging.error(e)
            return render(
                request,
                self.template_name,
                {
                    "project": project_id,
                    "error": "Error while uploading files to CLAM, please try again later",
                },
            )
        update_script(process.id)
        return redirect("scripts:g2p_loading", project_id=project_id)


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
        project_id = kwargs.get("project_id")
        try:
            project = Project.objects.filter(user=request.user.id).get(
                id=project_id
            )
        except Project.DoesNotExist:
            raise Http404("Project does not exist")

        if project.current_process.script != project.pipeline.g2p_script:
            raise Project.StateException(
                "Current project script is not a G2P script"
            )

        return render(
            request,
            self.template_name,
            {"process": project.current_process, "project": project},
        )


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
        project_id = kwargs.get("project_id")
        try:
            project = Project.objects.filter(user=request.user.id).get(
                id=project_id
            )
        except Project.DoesNotExist:
            raise Http404("Project does not exist")

        # Read content of file.
        content = project.get_oov_dict_file_contents()
        form = AlterDictionaryForm(initial={"dictionary": content})

        return render(
            request,
            self.template_name,
            {"form": form, "project_id": project.id,},
        )

    def post(self, request, **kwargs):
        """
        POST request of the check dictionary page.

        :param request: the request
        :param kwargs: keyword arguments
        :return: an Http404 response if the project_id is not found, a render of the check dictionary page if the
        AlterDictionaryForm is not valid, a redirect to the rerun FA page if the AlterDictionaryForm is valid
        """
        project_id = kwargs.get("project_id")
        try:
            project = Project.objects.filter(user=request.user.id).get(
                id=project_id
            )
        except Project.DoesNotExist:
            return Http404("Project does not exist")

        form = AlterDictionaryForm(request.POST)
        if form.is_valid():
            dictionary_content = form.cleaned_data.get("dictionary")
            project.write_oov_dict_file_contents(dictionary_content)
            print(project.current_process)

            project.current_process.remove_corresponding_profiles()
            project.current_process.delete()

            new_process = Process.create_process(
                project.pipeline.fa_script, project.folder
            )
            project.current_process = new_process
            project.save()
            profiles = Profile.objects.filter(process=new_process)

            # TODO select correct profile
            return redirect(
                "scripts:fa_start",
                project_id=project_id,
                profile_id=profiles[0],
            )
        else:
            return render(
                request,
                self.template_name,
                {"form": form, "project_id": project.id},
            )


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

            project = Project.create_project(
                project_name, pipeline, request.user
            )
            process = Process.create_process(pipeline.fa_script, project.folder)
            project.current_process = process
            project.save()
            return redirect("upload:upload_project", project_id=project.id)
        return render(
            request, self.template_name, {"form": form, "projects": projects},
        )


def download_project_archive(request, **kwargs):
    """Download the archive containing the process files."""
    project_id = kwargs.get("project_id")
    try:
        project = Project.objects.filter(user=request.user.id).get(
            id=project_id
        )
    except Project.DoesNotExist:
        raise Http404("Project does not exist")

    zip_filename = project.create_downloadable_archive()
    return serve(request, basename(zip_filename), dirname(zip_filename))
