import clam.common.client
import clam.common.data
import clam.common.status
from django.http import HttpResponseNotFound
from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from urllib.request import urlretrieve
from os import makedirs
from os.path import exists
from django.views.static import serve
from os.path import basename, dirname
from .models import Process, Profile, InputTemplate, Script
from django.http import JsonResponse


class ProcessOverview(TemplateView):
    """View for the process overview."""

    template_name = "process_overview.html"

    def get(self, request, **kwargs):
        """
        Render for get request for Process overview.

        :param request: the request from the user
        :param kwargs: keyword arguments
        :return: a render or HttpNotFound if the process_id does not exist
        """
        key = kwargs.get("process_id")
        try:
            process = Process.objects.get(pk=key)
            arg = self.create_argument(process)
            return render(request, self.template_name, arg)
        except Process.DoesNotExist:
            # TODO: Make a nice 404 page
            return HttpResponseNotFound("<h1>Page not found</h1>")

    def post(self, request, **kwargs):
        """
        Render for post request for Process overview.

        :param request: the request from the user
        :param kwargs: keyword arguments
        :return: a render or HttpNotFound if the process_id does not exist
        """
        if request.POST.get("form_handler") == "run_profile":
            profile_id = request.POST.get("profile_id")
            self.run_profile(profile_id, request.FILES)
            return redirect(request.GET.get("redirect"))

        key = kwargs.get("process_id")
        try:
            process = Process.objects.get(pk=key)
            arg = self.create_argument(process)
            return render(request, self.template_name, arg)
        except Process.DoesNotExist:
            # TODO: Make a nice 404 page
            return HttpResponseNotFound("<h1>Page not found</h1>")

    def create_argument(self, process):
        """
        Create argument set for rendering this page.

        :param process: the process object to render this page
        :return: an argument list containing the process, all its profiles and all the profiles' input templates
        """
        arg = {"process": process}
        arg["process"].profiles = Profile.objects.select_related().filter(
            process=arg["process"].id
        )
        for profile in arg["process"].profiles:
            profile.input_templates = InputTemplate.objects.select_related().filter(
                corresponding_profile=profile.id
            )
        return arg

    def run_profile(self, profile_id, files):
        """
        Run a specified process with the given profile.

        :param profile_id: the profile id to run
        :param files: the files to be uploaded to the CLAM server
        :return: None
        """
        profile = Profile.objects.get(pk=profile_id)
        argument_files = list()
        for input_template in InputTemplate.objects.select_related().filter(
            corresponding_profile=profile
        ):
            # TODO: This is now writing to the main directory, replace this with files from the uploaded files
            with open(
                files["template_id_{}".format(input_template.id)].name, "wb",
            ) as file:
                for chunk in files["template_id_{}".format(input_template.id)]:
                    file.write(chunk)

            argument_files.append(
                (
                    files["template_id_{}".format(input_template.id)].name,
                    input_template.template_id,
                )
            )

        process_to_run = Process.objects.get(pk=profile.process.id)
        clam_server = Script.objects.get(pk=process_to_run.script.id)
        clamclient = clam.common.client.CLAMClient(clam_server.hostname)
        # TODO: If a file is already uploaded, uploading files over it gives an error, therefor we remove the
        # project and recreate it. There might be a better way of doing this in the future
        clamclient.delete(process_to_run.clam_id)
        clamclient.create(process_to_run.clam_id)
        for (file, template) in argument_files:
            clamclient.addinputfile(process_to_run.clam_id, template, file)

        clamclient.startsafe(process_to_run.clam_id)


class CLAMFetch(TemplateView):
    """
    Download and serve files from CLAM.

    I initially did this by parsing XML, but this happens to be faster.
    """

    def get(self, request, **kwargs):
        """
        Nothing yet.

        :param request:
        :param kwargs:
        :return:
        """
        clam_id = kwargs.get("process")
        path = kwargs.get("p")
        process = Process.objects.get(clam_id=clam_id)

        save_file = "scripts/{}{}".format(clam_id, path)
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
        key = kwargs.get("process_id")
        process = Process.objects.get(pk=key)
        clam_server = Script.objects.get(pk=process.script.id)
        clamclient = clam.common.client.CLAMClient(clam_server.hostname)
        clam_info = clamclient.get(process.clam_id)
        return JsonResponse(
            {
                "status": clam_info.status,
                "status_message": clam_info.statusmessage,
                "errors": clam_info.errors,
                "error_message": clam_info.errormsg,
            }
        )
