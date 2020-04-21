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
        project = kwargs.get("project")

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
                    "scripts:g2p_start", project=project, profile=profile,
                )
            else:
                return redirect("scripts:cd_screen", project=project)
        elif project.current_process.script == project.pipeline.g2p_script:
            try:
                profile = Profile.objects.get(process=project.current_process)
            except Profile.MultipleObjectsReturned:
                # TODO: Make a nice error screen
                raise Profile.MultipleObjectsReturned
            return redirect(
                "scripts:g2p_start", project=project, profile=profile
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
        project = kwargs.get("project")
        profile = kwargs.get("profile")

        process = project.current_process
        if process.script != project.pipeline.fa_script:
            return render(
                request,
                self.template_name,
                {
                    "project": project.id,
                    "error": "Current process is not a Forced Alignment process",
                },
            )
        if profile.process != process:
            return render(
                request,
                self.template_name,
                {
                    "project": project.id,
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
                    "project": project.id,
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
                    "project": project.id,
                    "error": "Error while uploading files to CLAM, please try again later",
                },
            )
        update_script(process.id)
        return redirect("scripts:fa_loading", project=project)


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
        project = kwargs.get("project")

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
        project = kwargs.get("project")

        if project.finished_fa():
            return render(
                request,
                self.template_name,
                {"success": True, "project": project},
            )
        else:
            return render(
                request,
                self.template_name,
                {"success": False, "project": project},
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
        project = kwargs.get("project")
        profile = kwargs.get("profile")

        process = project.current_process
        if process.script != project.pipeline.g2p_script:
            print(process.script)
            return render(
                request,
                self.template_name,
                {
                    "project": project.id,
                    "error": "Current process is not a G2P process",
                },
            )
        if profile.process != process:
            return render(
                request,
                self.template_name,
                {
                    "project": project.id,
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
                    "project": project.id,
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
                    "project": project.id,
                    "error": "Error while uploading files to CLAM, please try again later",
                },
            )
        update_script(process.id)
        return redirect("scripts:g2p_loading", project=project)


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
        project = kwargs.get("project")

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
        project = kwargs.get("project")

        # Read content of file.
        content = project.get_oov_dict_file_contents()
        form = AlterDictionaryForm(initial={"dictionary": content})

        return render(
            request, self.template_name, {"form": form, "project": project,},
        )

    def post(self, request, **kwargs):
        """
        POST request of the check dictionary page.

        :param request: the request
        :param kwargs: keyword arguments
        :return: an Http404 response if the project_id is not found, a render of the check dictionary page if the
        AlterDictionaryForm is not valid, a redirect to the rerun FA page if the AlterDictionaryForm is valid
        """
        project = kwargs.get("project")

        form = AlterDictionaryForm(request.POST)
        if form.is_valid():
            dictionary_content = form.cleaned_data.get("dictionary")
            project.write_oov_dict_file_contents(dictionary_content)

            project.current_process.remove_corresponding_profiles()
            project.current_process.delete()

            new_process = Process.objects.create(
                script=project.pipeline.fa_script, folder=project.folder
            )
            project.current_process = new_process
            project.save()
            profiles = Profile.objects.filter(process=new_process)

            # TODO select correct profile
            return redirect(
                "scripts:fa_start", project=project, profile=profiles[0],
            )
        else:
            return render(
                request, self.template_name, {"form": form, "project": project},
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
        process = kwargs.get("process")
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
            process = Process.objects.create(script=pipeline.fa_script, folder=project.folder)
            project.current_process = process
            project.save()
            return redirect("upload:upload_project", project=project)
        return render(
            request, self.template_name, {"form": form, "projects": projects},
        )


def download_project_archive(request, **kwargs):
    """Download the archive containing the process files."""
    project = kwargs.get("project")

    zip_filename = project.create_downloadable_archive()
    return serve(request, basename(zip_filename), dirname(zip_filename))
