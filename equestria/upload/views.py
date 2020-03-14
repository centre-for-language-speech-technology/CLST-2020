import os
from django.conf import settings
from django.shortcuts import render
from django.views.generic import TemplateView
from .forms import UploadTXTForm, UploadWAVForm
from django.core.files.storage import FileSystemStorage

# Create your views here.


class UploadWAVView(TemplateView):
    """Page to upload a wav file."""

    template_name = "upload_wav2.html"

    def get(self, request):
        """Get request serves the page and loads the upload form."""
        form = UploadWAVForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        """Post request accepts a wav file and saves it on server."""
        form = UploadWAVForm(request.POST, request.FILES)
        wavfile = request.FILES["wavFile"]
        fs = FileSystemStorage(location="media/sname/wav")
        if fs.exists("txtFile"):
            os.remove(
                os.path.join(settings.MEDIA_ROOT + "/sname/wav", "wavFile")
            )
        fs.save("wavFile", wavfile)
        return render(request, self.template_name, {"form": form})


class UploadTXTView(TemplateView):
    """Page to upload a txt file."""

    template_name = "upload_wav2.html"

    def get(self, request):
        """Get request serves the page and loads the upload form."""
        form = UploadTXTForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        """Post request accepts a txt file and saves it on server."""
        form = UploadTXTForm(request.POST, request.FILES)
        txtfile = request.FILES["txtFile"]
        fs = FileSystemStorage(location="media/sname/txt")
        if fs.exists("txtFile"):
            os.remove(
                os.path.join(settings.MEDIA_ROOT + "/sname/txt", "txtFile")
            )
        fs.save("txtFile", txtfile)
        return render(request, self.template_name, {"form": form})


class UploadView(TemplateView):
    """Page to upload generic file."""

    template_name = "upload.html"

    def get(self, request):
        """Get request serves the page and loads the upload form."""
        form = UploadFileForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        """Post request accepts a file and saves it on server."""
        form = UploadFileForm(request.POST, request.FILES)
        f = request.FILES["f"]
        fs = FileSystemStorage()
        fs.save(f.name, f)
        return render(request, self.template_name, {"form": form})
