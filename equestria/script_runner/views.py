from django.http import HttpResponseNotFound
from django.views.generic import TemplateView
from django.shortcuts import render
from django.views.static import serve
from os.path import basename, dirname
from .models import Process, Profile, InputTemplate


class ProcessOverview(TemplateView):
    template_name = "process_overview.html"

    def get(self, request, **kwargs):
        key = kwargs.get("process")
        try:
            process = Process.objects.get(pk=key)
            arg = {"process": process}
            arg["process"].profiles = Profile.objects.select_related().filter(
                process=arg["process"].id
            )
            for profile in arg["process"].profiles:
                profile.input_templates = InputTemplate.objects.select_related().filter(
                    corresponding_profile=profile.id
                )
            return render(request, self.template_name, arg)
        except Process.DoesNotExist:
            # TODO: Make a nice 404 page
            return HttpResponseNotFound("<h1>Page not found</h1>")

    def get(self, request, output_file):
        """Respond to get request by serving requested output file."""
        return render(request, output_file)

    def post(self, request, output_file):
        """Respond to post request by serving requested output file."""
        return render(request, output_file)


class Downloads(TemplateView):
    """View to serve downloadable files."""

    def get(self, request, path):
        """Respond to get request by serving requested download file."""
        return serve(request, basename(path), dirname(path))

    def post(self, request, path):
        """Respond to post request by serving requested download file."""
        return serve(request, basename(path), dirname(path))
