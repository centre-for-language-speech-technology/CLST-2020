from django.shortcuts import render
from django.http import HttpResponseNotFound
from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.db.models import Q
from fancybar.models import PraatScripts
from script_runner.models import Script, Argument
# from .forms import UploadFileForm
from django.core.files.storage import FileSystemStorage
from upload import forms as uploadForms
from scripts.models import execute_script
from script_runner.constants import *
from script_runner import backend_interface


# Create your views here.


class GenericTemplate(TemplateView):
    template_name = 'template.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        return render(request, self.template_name)


class Fancybar(GenericTemplate):
    template_name = 'template.html'


class PraatScripts(TemplateView):
    template_name = 'praat_scripts.html'

    arg = {
        'scripts': Script.objects.all(),

        'USER_SPECIFIED_FILE': USER_SPECIFIED_FILE,
        'USER_SPECIFIED_TEXT': USER_SPECIFIED_TEXT,
        'USER_SPECIFIED_BOOL': USER_SPECIFIED_BOOL,
        'USER_SPECIFIED_INT':  USER_SPECIFIED_INT,
    }

    for s in arg["scripts"]:
        s.args = Argument.objects.select_related().filter(associated_script=s.id)

    def get(self, request):
        return render(request, self.template_name, self.arg)

    def post(self, request):
        name = request.POST.get("script_name", "")
        script_id = request.POST.get("script_id", "")
        args = []
        for argument in Argument.objects.select_related().filter(associated_script=script_id):
            args += [
                (argument, request.POST.get(
                    "script_{}_argument_{}".format(script_id, argument.id))),
            ]
        print('"Running" script ' + name + "...")
        print(args)
        backend_interface.run(
            Script.objects.get(pk=script_id), args)
        self.arg['script_run'] = name
        return render(request, self.template_name, self.arg)


class UploadWav(GenericTemplate):
    template_name = 'upload_wav.html'


class UploadTxt(GenericTemplate):
    template_name = 'upload_txt.html'


class ForcedAlignment(TemplateView):
    template_name = 'forced_alignment.html'

    def get(self, request):
        return render(request, self.template_name)

    def get(self, request):
        form = uploadForms.UploadFileForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = uploadForms.UploadFileForm(request.POST, request.FILES)
        f = request.FILES['f']
        fs = FileSystemStorage()
        fs.save(f.name, f)
        execute_script()
        return render(request, self.template_name)


class UpdateDictionary(GenericTemplate):
    template_name = 'update_dictionary.html'


class AutoSegmentation(GenericTemplate):
    template_name = 'auto_segmentation.html'


class DownloadResults(GenericTemplate):
    template_name = 'download_results.html'
