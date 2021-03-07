from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from guardian.mixins import LoginRequiredMixin
from guardian.shortcuts import assign_perm
from pipelines.models import Pipeline
from projects.forms import ProjectCreateForm
from projects.models import Project, File
from scripts.models import Profile

from .forms import UploadForm


class ProjectDetailView(LoginRequiredMixin, TemplateView):
    """View for initial upload of files to a project."""

    login_url = "/accounts/login/"

    template_name = "projects/project-detail.html"

    def get(self, request, **kwargs):
        """
        Handle a GET request for the file upload page.

        :param request: the request
        :param kwargs: keyword arguments
        :return: A render of the project detail page containing an upload form
        """
        project = kwargs.get("project")
        if not request.user.has_perm("access_project", project):
            raise PermissionDenied

        context = {
            "project": project,
            "profiles": Profile.objects.filter(
                script=project.pipeline.fa_script
            ),
            "upload_form": UploadForm(),
        }
        return render(request, self.template_name, context)


class ProjectOverview(LoginRequiredMixin, TemplateView):
    """Class to handle get requests to the project overview page."""

    login_url = "/accounts/login/"

    template_name = "projects/project-overview.html"

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
            project = Project.objects.create(
                name=project_name, pipeline=pipeline, user=request.user
            )
            assign_perm("access_project", request.user, project)
            return redirect("projects:project_detail", project=project)
        return render(
            request, self.template_name, {"form": form, "projects": projects},
        )


class CheckDictionaryScreen(LoginRequiredMixin, TemplateView):
    """Check dictionary page."""

    login_url = "/accounts/login/"

    template_name = "projects/check-dictionary-screen.html"

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

        return render(
            request,
            self.template_name,
            {
                "project": project,
                "dictionary_files": project.get_dictionary_files(),
            },
        )


class FAOverviewView(LoginRequiredMixin, TemplateView):
    """After the script is done, this screen shows the results."""

    login_url = "/accounts/login/"

    template_name = "projects/fa-overviewpage.html"

    def get(self, request, **kwargs):
        """
        GET request for FA overview page.

        :param request: the request
        :param kwargs: keyword arguments
        :return: a render of the FA overview page
        """
        project = kwargs.get("project")

        if not request.user == project.user:
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


class ProjectDeleteView(LoginRequiredMixin, TemplateView):
    """View for deleting projects."""

    template_name = "projects/project-delete.html"

    def get(self, request, **kwargs):
        """
        GET request for ProjectDeleteView.

        :param request: the request
        :param kwargs: keyword arguments
        :return: a render of the project-delete page
        """
        project = kwargs.get("project")

        if not request.user == project.user:
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
        return redirect("projects:overview")
