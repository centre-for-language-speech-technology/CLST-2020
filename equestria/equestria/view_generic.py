from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from accounts.models import UserProfile
from django.conf import settings


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


class RestrictedTemplate(GenericTemplate):
    """View to render a html page without any additional features that is login restricted."""

    def get(self, request):
        """Respond to get request."""
        if not request.user.is_authenticated:
            return redirect("%s?next=%s" % (settings.LOGIN_URL, request.path))
        else:
            return super().get(request)

    def post(self, request):
        """Respond to post request."""
        if not request.user.is_authenticated:
            return redirect("%s?next=%s" % (settings.LOGIN_URL, request.path))
        else:
            return super().get(request)
