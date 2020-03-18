import clam.common.client
import clam.common.data
import clam.common.status
from django.http import HttpResponseNotFound
from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from .models import Process, Profile, InputTemplate, Script


class ProcessOverview(TemplateView):
    """View for the process overview."""

    template_name = "process_overview.html"

    def get(self, request, **kwargs):
        """
        
        :param request:
        :param kwargs:
        :return:
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
