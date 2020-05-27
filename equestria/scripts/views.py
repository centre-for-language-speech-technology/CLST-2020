"""Module to handle uploading files."""
from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from os.path import basename, dirname
from django.views.static import serve
from .models import Project, Profile, Pipeline, BaseParameter, Process
from django.http import JsonResponse
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
)
from .forms import (
    ProjectCreateForm,
    AlterDictionaryForm,
    ProfileSelectForm,
    ParameterForm,
)
import logging
from django.urls import reverse
from guardian.shortcuts import assign_perm
from django.core.exceptions import PermissionDenied


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
        if not request.user.has_perm("access_project", project):
            raise PermissionDenied

        if (
            project.has_non_empty_extension_file([".oov"])
            and project.can_start_new_process()
        ):
            return redirect(
                "scripts:start_automatic", project, project.pipeline.g2p_script
            )
        elif project.can_start_new_process():
            return redirect("scripts:cd_screen", project=project)
        else:
            return render(request, self.template_name)


class AutomaticScriptStartView(LoginRequiredMixin, TemplateView):
    """Automatic start view for scripts."""

    login_url = "/accounts/login"

    template_name = "scripts/start-automatic.html"

    def get_render_multiple_profiles(
        self, request, project, script, profile_form
    ):
        """
        GET request for Automatic script start view for a render with multiple profiles.

        :param request: the request
        :param project: the project
        :param script: the script
        :param profile_form: the profile form
        :return: a render of the page with a profile form included
        """
        return render(
            request,
            self.template_name,
            {
                "form": profile_form,
                "message": "There are multiple profiles"
                " that can be applied to this"
                " project, please select one.",
                "project": project,
                "script": script,
            },
        )

    def get_render_no_profiles(self, request, project, script):
        """
        GET request for Automatic script start view for a render with no profiles.

        :param request: the request
        :param project: the project
        :param script: the script
        :return: a render of the page without a profile form included
        """
        return render(
            request,
            self.template_name,
            {
                "message": "There are no profiles that can be applied to this"
                " project, did you upload all required files?",
                "project": project,
                "script": script,
            },
        )

    def get(self, request, **kwargs):
        """
        GET method for the automatic start screen of FA.

        :param request: the request
        :param kwargs: the keyword arguments
        :return: a redirect to the script start view if only one profile matches, otherwise a form to select a profile
        for the user
        """
        project = kwargs.get("project")
        script = kwargs.get("script")

        if not request.user.has_perm("access_project", project):
            raise PermissionDenied
        if not project.is_project_script(script):
            raise ValueError("Script is not a project script")

        valid_profiles = script.get_valid_profiles(project.folder)
        if len(valid_profiles) > 1:
            profile_form = ProfileSelectForm(
                request.POST, profiles=valid_profiles
            )
            return self.get_render_multiple_profiles(
                request, project, script, profile_form
            )
        elif len(valid_profiles) == 0:
            return self.get_render_no_profiles(request, project, script)
        else:
            profile = valid_profiles[0]
            return redirect(
                "scripts:start", project=project, profile=profile, script=script
            )

    def post(self, request, **kwargs):
        """
        POST method for automatic start screen of FA.

        :param request: the request
        :param kwargs: keyword arguments
        :return: a redirect to the fa start view if a correct profile is selected, otherwise a form to select a profile
        for the user
        """
        project = kwargs.get("project")
        script = kwargs.get("script")

        if not project.is_project_script(script):
            raise ValueError("Script is not a project script")

        valid_profiles = project.pipeline.fa_script.get_valid_profiles(
            project.folder
        )
        profile_form = ProfileSelectForm(request.POST, profiles=valid_profiles)
        if profile_form.is_valid():
            profile = Profile.objects.get(
                pk=profile_form.cleaned_data.get("profile")
            )
            return redirect(
                "scripts:start", project=project, profile=profile, script=script
            )
        else:
            return self.get_render_multiple_profiles(
                request, project, script, profile_form
            )


class ScriptStartView(LoginRequiredMixin, TemplateView):
    """Start screen for a script."""

    login_url = "/accounts/login/"

    template_name = "scripts/start-screen.html"

    @staticmethod
    def get_redirect_link(project, script):
        """
        Get the redirect link for a specific project or script (the page of the project status).

        :param project: the project
        :param script: the script
        :return: a tag for the redirect link
        """
        if script == project.pipeline.fa_script:
            return "scripts:loading"
        elif script == project.pipeline.g2p_script:
            return "scripts:loading"
        else:
            raise ValueError("Script is not FA script or G2P script")

    def get(self, request, **kwargs):
        """
        GET method for the start screen of G2P.

        :param request: the request
        :param kwargs: the keyword arguments
        :return: a redirect to the g2p loading screen if the process could be started successfully, returns a render of
        the g2p-start-screen.html template with an error message if an error occurred
        """
        project = kwargs.get("project")
        profile = kwargs.get("profile")
        script = kwargs.get("script")

        if not request.user.has_perm("access_project", project):
            raise PermissionDenied
        if not project.is_project_script(script):
            raise ValueError("Script is not a project script")

        redirect_link = self.get_redirect_link(project, script)

        variable_parameters = script.get_variable_parameters()
        parameter_form = ParameterForm(variable_parameters)

        started, error = start_script_get_error(script, project, profile,)
        if started:
            return redirect(redirect_link, project=project, script=script)
        else:
            return render(
                request,
                self.template_name,
                {
                    "project": project,
                    "error": error,
                    "parameter_form": parameter_form,
                    "script": script,
                },
            )

    def post(self, request, **kwargs):
        """
        POST method for the start screen of G2P.

        :param request: the request
        :param kwargs: the keyword arguments
        :return: a redirect to the g2p loading screen if the process could be started successfully, returns a render of
        the g2p-start-screen.html template with an error message if an error occurred
        """
        project = kwargs.get("project")
        profile = kwargs.get("profile")
        script = kwargs.get("script")

        if not project.is_project_script(script):
            raise ValueError("Script is not a project script")

        redirect_link = self.get_redirect_link(project, script)

        variable_parameters = script.get_variable_parameters()
        if len(variable_parameters) > 0:
            parameter_form = ParameterForm(variable_parameters, request.POST)
        else:
            parameter_form = None

        started, error = start_script_get_error(
            script,
            project,
            profile,
            parameters=parameter_form.cleaned_data
            if parameter_form.is_valid()
            else None,
        )
        if started:
            return redirect(redirect_link, project=project, script=script)
        else:
            return render(
                request,
                self.template_name,
                {
                    "project": project,
                    "error": error,
                    "parameter_form": parameter_form,
                    "script": script,
                },
            )


class ScriptLoadScreen(LoginRequiredMixin, TemplateView):
    """
    Loading indicator for Forced Alignment.

    This class shows the loading status to the user
    If needed, it launches a new process. If the user refreshes this page
    and a FA script is already running, it wont start a new process.
    """

    login_url = "/accounts/login/"

    template_name = "scripts/loadingscreen.html"

    @staticmethod
    def get_continue_link(project, script):
        """
        Get a continue link for a project and script.

        :param project: the project
        :param script: the script
        :return: a tag for the next page
        """
        if script == project.pipeline.fa_script:
            return "scripts:fa_redirect"
        elif script == project.pipeline.g2p_script:
            return "scripts:cd_screen"
        else:
            raise ValueError("Script does not correspond to project")

    def get(self, request, **kwargs):
        """
        GET request for fa loading page.

        :param request: the request
        :param kwargs: keyword arguments
        :return: a render of the fa loading screen
        """
        project = kwargs.get("project")
        script = kwargs.get("script")

        if not request.user.has_perm("access_project", project):
            raise PermissionDenied
        if not project.is_project_script(script):
            raise ValueError("Script is not a project script")

        return render(
            request, self.template_name, {"project": project, "script": script},
        )

    def post(self, request, **kwargs):
        """
        POST request for the fa loading page.

        :param request: the request
        :param kwargs: keyword arguments
        :return: removes a finished process from a project and then redirects to the fa redirect screen. If the
        project has no running process, the user will be redirected to the change dictionary screen as well. If the
        process of the project is not finished yet, this function raises a Project.StateException
        """
        project = kwargs.get("project")
        script = kwargs.get("script")

        if not project.is_project_script(script):
            raise ValueError("Script is not a project script")

        continue_link = self.get_continue_link(project, script)

        if project.current_process is None:
            return redirect(continue_link, project=project)
        if project.current_process.script != script:
            raise Project.StateException(
                "Current project script is not the corresponding script"
            )

        if project.current_process.is_finished():
            project.cleanup()
            return redirect(continue_link, project=project)
        else:
            raise Project.StateException("Current process is not finished yet")


class FAOverview(LoginRequiredMixin, TemplateView):
    """After the script is done, this screen shows the results."""

    login_url = "/accounts/login/"

    template_name = "scripts/fa-overviewpage.html"

    def get(self, request, **kwargs):
        """
        GET request for FA overview page.

        :param request: the request
        :param kwargs: keyword arguments
        :return: a render of the FA overview page
        """
        project = kwargs.get("project")

        if not request.user.has_perm("access_project", project):
            raise PermissionDenied

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


class CheckDictionaryScreen(LoginRequiredMixin, TemplateView):
    """Check dictionary page."""

    login_url = "/accounts/login/"

    template_name = "scripts/check-dictionary-screen.html"

    def get(self, request, **kwargs):
        """
        GET request for the check dictionary page.

        :param request: the request
        :param kwargs: keyword arguments
        :return: a render of the check dictionary page
        """
        project = kwargs.get("project")

        if not request.user.has_perm("access_project", project):
            raise PermissionDenied
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

            return redirect(
                "scripts:start_automatic",
                project=project,
                script=project.pipeline.fa_script,
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

    template_name = "scripts/project-overview.html"

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
            assign_perm("access_project", request.user, project)
            return redirect("upload:upload_project", project=project)
        return render(
            request, self.template_name, {"form": form, "projects": projects},
        )


class ProjectDeleteView(LoginRequiredMixin, TemplateView):
    """View for deleting projects."""

    template_name = "scripts/project-delete.html"

    def get(self, request, **kwargs):
        """
        GET request for ProjectDeleteView.

        :param request: the request
        :param kwargs: keyword arguments
        :return: a render of the project-delete page
        """
        project = kwargs.get("project")

        if not request.user.has_perm("access_project", project):
            raise PermissionDenied

        return render(request, self.template_name, {"project": project})

    def post(self, request, **kwargs):
        """
        POST request for ProjectDeleteView.

        Deletes a project and redirects to the project overview page
        :param request: the request
        :param kwargs: keyword arguments
        :return: a redirect to the project overview page
        """
        project = kwargs.get("project")
        project.delete()
        return redirect("scripts:projects")


def start_script_get_error(script_to_start, project, profile, parameters=None):
    """
    Render a start screen.

    This method is used by the FA start screen and the G2P start screen. This method tries to start a script and return
    the process on success.
    :param parameters: a form for setting variable parameters
    :param script_to_start: the script to start
    :param project: the project to use
    :param profile: the profile to use
    :return: a Process object if the script was started successfully. A render of the template_name page with a
    corresponding error message if starting of the script failed
    """
    try:
        if parameters is not None:
            project.start_script(
                profile, script_to_start, parameter_values=parameters,
            )
        else:
            project.start_script(profile, script_to_start)
        return True, ""
    except BaseParameter.ParameterException:
        error = "Not all script parameters are filled in"
    except Project.StateException:
        error = "There is already a running process for this project"
    except Profile.IncorrectProfileException:
        error = "Invalid profile for running this script"
    except ValueError:
        error = "Error while starting the process, make sure all input files are specified"
    except Exception:
        error = "Error while uploading files to CLAM, please try again later"

    return False, error


def download_project_archive(request, **kwargs):
    """
    Download all files of a project in ZIP format.

    :param request: the request
    :param kwargs: keyword arguments
    :return: a serve of a compressed archive of the project folder (ZIP format)
    """
    project = kwargs.get("project")

    zip_filename = project.create_downloadable_archive()
    return serve(request, basename(zip_filename), dirname(zip_filename))
