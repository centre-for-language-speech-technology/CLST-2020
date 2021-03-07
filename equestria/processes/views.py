from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import render

from django.views.generic import TemplateView


class ProcessDetailView(LoginRequiredMixin, TemplateView):
    """
    Loading indicator for Forced Alignment.

    This class shows the loading status to the user
    If needed, it launches a new process. If the user refreshes this page
    and a FA script is already running, it wont start a new process.
    """

    login_url = "/accounts/login/"

    template_name = "processes/process-detail.html"

    def get(self, request, **kwargs):
        """
        GET request for fa loading page.

        :param request: the request
        :param kwargs: keyword arguments
        :return: a render of the fa loading screen
        """
        process = kwargs.get("process")
        if not process.project.user == request.user:
            raise PermissionDenied

        return render(
            request,
            self.template_name,
            {"process": process, "project": process.project},
        )


class FAProcessOverviewView(LoginRequiredMixin, TemplateView):
    """Overview view for FA processes."""

    login_url = "/accounts/login/"

    template_name = "processes/process-overview.html"

    def get(self, request, **kwargs):
        """
        GET request for process overview page.

        :param request: the request
        :param kwargs: keyword arguments
        :return: a render of the process overview page
        """
        project = kwargs.get("project")
        return render(
            request,
            self.template_name,
            {"project": project, "script_type": "FA"},
        )


class G2PProcessOverviewView(LoginRequiredMixin, TemplateView):
    """Overview view for G2P processes."""

    login_url = "/accounts/login/"

    template_name = "processes/process-overview.html"

    def get(self, request, **kwargs):
        """
        GET request for process overview page.

        :param request: the request
        :param kwargs: keyword arguments
        :return: a render of the process overview page
        """
        project = kwargs.get("project")
        return render(
            request,
            self.template_name,
            {"project": project, "script_type": "G2P"},
        )
