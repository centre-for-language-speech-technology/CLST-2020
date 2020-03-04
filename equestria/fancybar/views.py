from django.shortcuts import render
from django.http import HttpResponseNotFound
from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.db.models import Q
from fancybar.models import *
# from .forms import UploadFileForm
from django.core.files.storage import FileSystemStorage
from upload import forms as uploadForms
from scripts.models import execute_script


# Create your views here.


class GenericTemplate(TemplateView):
    template_name = 'template.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        print(request)
        return render(request, self.template_name)


class Fancybar(GenericTemplate):
    template_name = 'template.html'


class PraatScripts(TemplateView):
    template_name = 'praat_scripts.html'

    arg = {
        'scripts': PraatScripts.objects.all(),
    }

    def get(self, request):
        return render(request, self.template_name, self.arg)

    def post(self, request):
        name = request.POST.get("script_name", "")
        print('"Running" script ' + name + "...")
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
