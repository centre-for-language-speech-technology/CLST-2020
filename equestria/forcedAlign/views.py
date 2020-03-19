import os
from django.conf import settings
from django.shortcuts import render
from django.views.generic import TemplateView
from upload.forms import UploadTXTForm, UploadWAVForm
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponseRedirect

# Create your views here.


class FAView(TemplateView):
    """Class to handle get requests to the forced alignment page"""

    template_name = "ForcedAlign.html"

    def get(self, request):
        """
        Function to handle get requests to the forced alignment page
        returning the html file with two upload forms from upload.forms
        with callback URLs upload/wav and upload/txt
        """
        wavForm = UploadWAVForm()
        txtForm = UploadTXTForm()
        return render(
            request,
            self.template_name,
            {"WAVform": wavForm, "TXTform": txtForm},
        )
