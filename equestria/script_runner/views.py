from django.views.generic import TemplateView
from django.shortcuts import render

# Create your views here.


class Outputs(TemplateView):
    """View to serve output files."""

    def get(self, request, output_file):
        """Respond to get request by serving requested output file."""
        return render(request, output_file)

    def post(self, request, output_file):
        """Respond to post request by serving requested output file."""
        return render(request, output_file)
