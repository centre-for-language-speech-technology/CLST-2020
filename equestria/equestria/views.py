from equestria.view_generic import *


class WelcomePage(TemplateView):
    """Page to greet the user."""

    template_name = "equestria/welcome.html"

    def get(self, request, **kwargs):
        """
        GET request for WelcomePage.

        :param request: the request
        :param kwargs: keyword arguments
        :return: a render of the welcome page
        """
        context = {"admin_email": settings.ADMIN_EMAIL}
        return render(request, self.template_name, context)
