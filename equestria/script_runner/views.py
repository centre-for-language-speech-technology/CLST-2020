from django.views.generic import TemplateView
from django.shortcuts import render
from django.views.static import serve
from os.path import basename, dirname

# Create your views here.


class Outputs(TemplateView):
    """View to serve output files."""

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
