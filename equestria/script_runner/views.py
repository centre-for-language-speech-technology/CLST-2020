from django.http import HttpResponseNotFound
from django.views.generic import TemplateView
from django.shortcuts import render
from .models import Process, Profile, InputTemplate


class ProcessOverview(TemplateView):
    template_name = "process_overview.html"

    def get(self, request, **kwargs):
        key = kwargs.get('process')
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
            return HttpResponseNotFound('<h1>Page not found</h1>')

