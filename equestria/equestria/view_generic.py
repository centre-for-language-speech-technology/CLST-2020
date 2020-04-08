from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from accounts.models import UserProfile
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin


class GenericTemplate(TemplateView):
    """View to render a html page without any additional features."""

    template_name = "template.html"

    def __get_profile(self, request):
        """Retrieve profile based on user in request."""
        user_profile = (
            UserProfile.objects.select_related()
            .filter(user_id=request.user.id)
            .first()
        )
        return user_profile

    def get(self, request):
        """Respond to get request."""
        return render(request, self.template_name)

    def post(self, request):
        """Respond to post request."""
        return render(request, self.template_name)


class RestrictedTemplate(LoginRequiredMixin, GenericTemplate):
    """View to render a html page without any additional features that is login restricted."""

    login_url = "/accounts/login/"
    redirect_field_name = "redirect_to"

    def get(self, request):
        """Respond to get request."""
        return super().get(request)

    def post(self, request):
        """Respond to post request."""
        return super().get(request)
