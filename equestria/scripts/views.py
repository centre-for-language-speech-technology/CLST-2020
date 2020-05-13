"""Module to handle uploading files."""
from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from os.path import basename, dirname
from django.views.static import serve
from .models import Project, Profile, Pipeline, BaseParameter, Process
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import (
    ProjectCreateForm,
    AlterDictionaryForm,
    ProfileSelectForm,
    ParameterForm,
)
from .tasks import update_script
import logging
from django.urls import reverse
from guardian.shortcuts import assign_perm


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

        if project.can_start_new_process():
            if project.has_non_empty_extension_file([".oov"]):
                try:
                    profile = Profile.objects.get(
                        script=project.pipeline.g2p_script
                    )
                except Profile.MultipleObjectsReturned:
                    # TODO: Make a nice error screen
                    raise Profile.MultipleObjectsReturned
                return redirect(
                    "scripts:g2p_start", project=project, profile=profile,
                )
            else:
                return redirect("scripts:cd_screen", project=project)
        elif (
            project.current_process is not None
            and project.current_process.script == project.pipeline.g2p_script
        ):
            try:
                profile = Profile.objects.get(process=project.current_process)
            except Profile.MultipleObjectsReturned as e:
                # TODO: Make a nice error screen
                raise e
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
        GET method for the start screen of FA.

        :param request: the request
        :param kwargs: the keyword arguments
        :return: a redirect to the fa loading screen if the process could be started successfully, returns a render of
        the fa-startscreen.html template with an error message if an error occurred
        """
        project = kwargs.get("project")
        profile = kwargs.get("profile")

        variable_parameters = (
            project.pipeline.fa_script.get_variable_parameters()
        )
        if len(variable_parameters) > 0:
            parameter_form = ParameterForm(variable_parameters)
        else:
            parameter_form = None

        process_or_view = render_start_screen(
            request,
            self.template_name,
            parameter_form,
            project.pipeline.fa_script,
            project,
            profile,
        )
        if isinstance(process_or_view, Process):
            update_script(process_or_view.id)
            return redirect("scripts:fa_loading", project=project)
        else:
            return process_or_view

    def post(self, request, **kwargs):
        """
        POST method for the start screen of FA.

        :param request: the request
        :param kwargs: the keyword arguments
        :return: a redirect to the fa loading screen if the process could be started successfully, returns a render of
        the fa-startscreen.html template with an error message if an error occurred
        """
        project = kwargs.get("project")
        profile = kwargs.get("profile")

        variable_parameters = (
            project.pipeline.fa_script.get_variable_parameters()
        )
        if len(variable_parameters) > 0:
            parameter_form = ParameterForm(variable_parameters, request.POST)
        else:
            parameter_form = None

        process_or_view = render_start_screen(
            request,
            self.template_name,
            parameter_form,
            project.pipeline.fa_script,
            project,
            profile,
        )
        if isinstance(process_or_view, Process):
            update_script(process_or_view.id)
            return redirect("scripts:fa_loading", project=project)
        else:
            return process_or_view


class FAStartAutomaticView(LoginRequiredMixin, TemplateView):
    """Automatic start view for Forced Alignment."""

    login_url = "/accounts/login/"

    template_name = "fa-start-automatic.html"

    def get(self, request, **kwargs):
        """
        GET method for the automatic start screen of FA.

        :param request: the request
        :param kwargs: the keyword arguments
        :return: a redirect to the fa start view if only one profile matches, otherwise a form to select a profile for
        the user
        """
        project = kwargs.get("project")
        valid_profiles = project.pipeline.fa_script.get_valid_profiles(
            project.folder
        )
        if len(valid_profiles) > 1:
            profile_form = ProfileSelectForm(
                request.POST, profiles=valid_profiles
            )
            return render(
                request,
                self.template_name,
                {
                    "form": profile_form,
                    "message": "There are multiple profiles"
                    " that can be applied to this"
                    " project, please select one.",
                    "project": project,
                },
            )
        elif len(valid_profiles) == 0:
            return render(
                request,
                self.template_name,
                {
                    "message": "There are no profiles that can be applied to this"
                    " project, did you upload all required files?",
                    "project": project,
                },
            )
        else:
            profile = valid_profiles[0]
            return redirect(
                "scripts:fa_start", project=project, profile=profile
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
        valid_profiles = project.pipeline.fa_script.get_valid_profiles(
            project.folder
        )

        profile_form = ProfileSelectForm(request.POST, profiles=valid_profiles)
        if profile_form.is_valid():
            profile = Profile.objects.get(
                pk=profile_form.cleaned_data.get("profile")
            )
            return redirect(
                "scripts:fa_start", project=project, profile=profile
            )
        else:
            return render(
                request,
                self.template_name,
                {
                    "form": profile_form,
                    "message": "There are multiple profiles"
                    " that can be applied to this"
                    " project, please select one.",
                    "project": project,
                },
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
        GET request for fa loading page.

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
        if project.current_process is None:
            return redirect("scripts:fa_redirect", project=project)
        if project.current_process.script != project.pipeline.fa_script:
            raise Project.StateException(
                "Current project script is no forced alignment script"
            )

        if project.current_process.is_finished():
            project.cleanup()
            return redirect("scripts:fa_redirect", project=project)
        else:
            raise Project.StateException("Current process is not finished yet")


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
        :return: a redirect to the g2p loading screen if the process could be started successfully, returns a render of
        the g2p-startscreen.html template with an error message if an error occurred
        """
        project = kwargs.get("project")
        profile = kwargs.get("profile")

        variable_parameters = (
            project.pipeline.g2p_script.get_variable_parameters()
        )
        parameter_form = ParameterForm(variable_parameters)

        process_or_view = render_start_screen(
            request,
            self.template_name,
            parameter_form,
            project.pipeline.g2p_script,
            project,
            profile,
        )
        if isinstance(process_or_view, Process):
            update_script(process_or_view.id)
            return redirect("scripts:g2p_loading", project=project)
        else:
            return process_or_view

    def post(self, request, **kwargs):
        """
        POST method for the start screen of G2P.

        :param request: the request
        :param kwargs: the keyword arguments
        :return: a redirect to the g2p loading screen if the process could be started successfully, returns a render of
        the g2p-startscreen.html template with an error message if an error occurred
        """
        project = kwargs.get("project")
        profile = kwargs.get("profile")

        variable_parameters = (
            project.pipeline.g2p_script.get_variable_parameters()
        )
        if len(variable_parameters) > 0:
            parameter_form = ParameterForm(variable_parameters, request.POST)
        else:
            parameter_form = None

        process_or_view = render_start_screen(
            request,
            self.template_name,
            parameter_form,
            project.pipeline.g2p_script,
            project,
            profile,
        )
        if isinstance(process_or_view, Process):
            update_script(process_or_view.id)
            return redirect("scripts:g2p_loading", project=project)
        else:
            return process_or_view


class G2PLoadScreen(LoginRequiredMixin, TemplateView):
    """Loading screen, where the g2p is run as well."""

    login_url = "/accounts/login/"

    template_name = "g2p-loadingscreen.html"

    def get(self, request, **kwargs):
        """
        GET request for loading page.

        :param request: the request
        :param kwargs: keyword arguments
        :return: a render of the fa loading screen
        """
        project = kwargs.get("project")

        if project.current_process.script != project.pipeline.g2p_script:
            raise Project.StateException(
                "Current project script is no g2p script"
            )

        return render(
            request,
            self.template_name,
            {"process": project.current_process, "project": project},
        )

    def post(self, request, **kwargs):
        """
        POST request for the loading page.

        :param request: the request
        :param kwargs: keyword arguments
        :return: removes a finished process from a project and then redirects to the change dictionary screen. If the
        project has no running process, the user will be redirected to the change dictionary screen as well. If the
        process of the project is not finished yet, this function raises a Project.StateException
        """
        project = kwargs.get("project")
        if project.current_process is None:
            return redirect("scripts:cd_screen", project=project)
        if project.current_process.script != project.pipeline.g2p_script:
            raise Project.StateException(
                "Current project script is no g2p script"
            )

        if project.current_process.is_finished():
            project.cleanup()
            return redirect("scripts:cd_screen", project=project)
        else:
            raise Project.StateException("Current process is not finished yet")


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

            profiles = Profile.objects.filter(script=project.pipeline.fa_script)

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

    @staticmethod
    def convert_to_view(project):
        """
        Get the view corresponding to the current project status of a project.

        :param project: the project
        :return: a reverse of the view that the user last left the project with
        """
        next_step = project.get_next_step()
        if next_step == Project.UPLOADING:
            return reverse("upload:upload_project", kwargs={"project": project})
        elif next_step == Project.FA_RUNNING:
            return reverse("scripts:fa_loading", kwargs={"project": project})
        elif next_step == Project.G2P_RUNNING:
            return reverse("scripts:g2p_loading", kwargs={"project": project})
        elif next_step == Project.CHECK_DICTIONARY:
            return reverse("scripts:cd_screen", kwargs={"project": project})
        else:
            raise ValueError("Value of next_step unknown")

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
        for project in projects:
            project.next_url = ProjectOverview.convert_to_view(project)
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
            assign_perm(
                    "access",
                    request.user,
                    request,
                )

            project = Project.create_project(
                project_name, pipeline, request.user
            )
            return redirect("upload:upload_project", project=project)
        return render(
            request, self.template_name, {"form": form, "projects": projects},
        )


class ProjectDeleteView(LoginRequiredMixin, TemplateView):
    """View for deleting projects."""

    template_name = "project-delete.html"

    def get(self, request, **kwargs):
        """
        GET request for ProjectDeleteView.

        :param request: the request
        :param kwargs: keyword arguments
        :return: a render of the project-delete page
        """
        project = kwargs.get("project")

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


def render_start_screen(
    request, template_name, parameter_form, script_to_start, project, profile
):
    """
    Render a start screen.

    This method is used by the FA start screen and the G2P start screen. This method tries to start a script and return
    the process on success.
    :param request: the request
    :param template_name: the template to render (this must be a start screen template)
    :param parameter_form: a form for setting variable parameters
    :param script_to_start: the script to start
    :param project: the project to use
    :param profile: the profile to use
    :return: a Process object if the script was started successfully. A render of the template_name page with a
    corresponding error message if starting of the script failed
    """
    try:
        if parameter_form is not None and parameter_form.is_valid():
            return project.start_script(
                profile,
                script_to_start,
                parameter_values=parameter_form.cleaned_data,
            )
        else:
            return project.start_script(profile, script_to_start)
    except BaseParameter.ParameterException as e:
        logging.error(e)
        error = "Not all script parameters are filled in"
    except Project.StateException as e:
        logging.error(e)
        error = "There is already a running process for this project"
    except Profile.IncorrectProfileException as e:
        logging.error(e)
        error = "Invalid profile for running this script"
    except ValueError as e:
        logging.error(e)
        error = "Error while starting the process, make sure all input files are specified"
    except Exception as e:
        logging.error(e)
        error = "Error while uploading files to CLAM, please try again later"

    return render(
        request,
        template_name,
        {"project": project, "error": error, "parameter_form": parameter_form,},
    )


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
