import os
from django.conf import settings
from django.shortcuts import render
from django.views.generic import TemplateView
from .forms import UploadTXTForm, UploadWAVForm
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponseRedirect


class UploadWAVView(TemplateView):
    """View for uploading wav files."""

    template_name = "upload_wav2.html"

    def get(self, request):
        """Load form and process request."""
        form = UploadWAVForm()
        return render(request, self.template_name, {"WAVform": form})

    def post(self, request):
        """Validate form and save it."""
        form = UploadWAVForm(request.POST, request.FILES)
        if form.is_valid():
            print("valid form")
            wavfile = request.FILES["wavFile"]
            fs = FileSystemStorage(location="media/sname/wav")
            if fs.exists(wavfile.name):
                os.remove(
                    os.path.join(
                        settings.MEDIA_ROOT + "/sname/wav", wavfile.name
                    )
                )
            fs.save(wavfile.name, wavfile)
        else:
            print("invalid form")
            print(form.errors)
            # return error to AJAX function to print
        return HttpResponseRedirect("/forced/")


class UploadTXTView(TemplateView):
    """View for uploading txt file."""

    template_name = "upload_txt2.html"

    def get(self, request):
        """Load form and process request."""
        form = UploadTXTForm()
        return render(request, self.template_name, {"TXTform": form})

    def post(self, request):
        """Validate form and save it."""
        form = UploadTXTForm(request.POST, request.FILES)
        if form.is_valid():
            print("valid form")
            txtfile = request.FILES["txtFile"]
            fs = FileSystemStorage(location="media/sname/txt")
            if fs.exists(txtfile.name):
                os.remove(
                    os.path.join(
                        settings.MEDIA_ROOT + "/sname/txt", txtfile.name
                    )
                )
            fs.save(txtfile.name, txtfile)
        else:
            print("invalid form")
            print(form.errors)
            # return error to AJAX function to print
        return HttpResponseRedirect("/forced/")
