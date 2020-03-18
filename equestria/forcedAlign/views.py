import os
from django.conf import settings
from django.shortcuts import render
from django.views.generic import TemplateView
from upload.forms import UploadTXTForm, UploadWAVForm
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponseRedirect

# Create your views here.


class FAView(TemplateView):

    template_name = "ForcedAlign.html"

    def get(self, request):
        """ Returns the rendering of this FA page. """
        wavForm = UploadWAVForm()
        txtForm = UploadTXTForm()
        return render(
            request,
            self.template_name,
            {"WAVform": wavForm, "TXTform": txtForm},
        )
