from django.http import HttpResponseNotFound
from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from .models import Process, Profile, InputTemplate
from urllib.request import urlretrieve
from os import makedirs
from os.path import dirname, exists
from django.views.static import serve
from os.path import basename, dirname


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


class CLAMFetch(TemplateView):
    """
    Download and serve files from CLAM

    I initially did this by parsing XML, but this happens to be faster
    """

    def get(self, request, **kwargs):
        clam_id = kwargs.get("process")
        path = kwargs.get("p")
        process = Process.objects.get(clam_id=clam_id)

        save_file = "outputs/{}{}".format(clam_id, path)
        print(save_file)
        print("{}/{}/output{}".format(process.script.hostname, clam_id, path))
        if not exists(dirname(save_file)):
            makedirs(dirname(save_file))
        urlretrieve(
            "{}/{}/output{}".format(process.script.hostname, clam_id, path),
            save_file,
        )
        return redirect(
            "script_runner:clam", path="outputs/{}/{}".format(clam_id, path),
        )


class Downloads(TemplateView):
    """View to serve downloadable files."""

    def get(self, request, path):
        """Respond to get request by serving requested download file."""
        return serve(request, basename(path), dirname(path))

    def post(self, request, path):
        """Respond to post request by serving requested download file."""
        return serve(request, basename(path), dirname(path))
