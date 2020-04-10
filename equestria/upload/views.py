import os
from django.conf import settings
from django.shortcuts import render
from django.views.generic import TemplateView
from .models import File
from .forms import UploadTXTForm, UploadWAVForm
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
import mimetypes

"""Module to handle uploading files."""


class UploadProjectView(TemplateView):
    """View for initial upload of files to a project."""

    template_name = "upload/upload-project.html"


def getFileType(path):
    """Get the file type of the uploaded file and categorize."""
    mime = mimetypes.guess_type(path)
    return mime[0]


def makeDBEntry(request, path, useFor):
    """Create an entry in the Database for the uploaded file."""
    file = File()
    file.owner = request.user.username
    file.path = path
    file.filetype = getFileType(path)
    file.usage = useFor
    file.save()


def safeFile(request, form, filetype, useFor):
    """Safe uploaded file."""
    username = request.user.username
    uploadedfile = request.FILES[filetype]
    path = os.path.join("media", username, filetype)
    absolutePath = os.path.join(
        settings.MEDIA_ROOT, username, filetype, uploadedfile.name
    )
    fs = FileSystemStorage(location=path)

    if fs.exists(uploadedfile.name):
        """Delete previously uploaded file with same name."""
        os.remove(absolutePath)

    makeDBEntry(request, absolutePath, useFor)
    fs.save(uploadedfile.name, uploadedfile)


class UploadWAVView(LoginRequiredMixin, TemplateView):
    """Handle the upload/wav page.

    Also acts as callback URL for the uploads in forced alignment page.
    """

    """View for uploading wav files."""

    login_url = "/accounts/login/"
    redirect_field_name = "redirect_to"

    template_name = "upload_wav2.html"

    def get(self, request):
        """Handle GET requests to upload/wav."""
        form = UploadWAVForm()
        return render(request, self.template_name, {"WAVform": form})

    def post(self, request):
        """Handle POST requests to upload/wav.

        Also acts as callback function from forced alignment page.
        """
        form = UploadWAVForm(request.POST, request.FILES)
        if form.is_valid():
            safeFile(request, form, "wavFile", "audio")
        else:
            print("invalid form")
            print(form.errors)
            # return error to AJAX function to print
        return HttpResponseRedirect("/accounts/overview/")


class UploadTXTView(LoginRequiredMixin, TemplateView):
    """Handle the upload/txt page.

    Also acts as callback URL for the uploads in forced alignment page.
    """

    login_url = "/accounts/login/"
    redirect_field_name = "redirect_to"

    template_name = "upload_txt2.html"

    #    def safeFile(self,request,form):
    #        """Function to safe uploaded txt file"""
    #        print("valid form")
    #        txtfile = request.FILES["txtFile"]
    #        fs = FileSystemStorage(location="media/sname/txt")
    #        if fs.exists(txtfile.name):
    #            os.remove(
    #                os.path.join(
    #                    settings.MEDIA_ROOT + "/sname/txt", txtfile.name
    #                )
    #            )
    #        fs.save(txtfile.name, txtfile)

    def get(self, request):
        """Handle GET requests to upload/txt."""
        form = UploadTXTForm()
        return render(request, self.template_name, {"TXTform": form})

    def post(self, request):
        """Handle POST requests to upload/txt.

        Also acts as callback function from forced alignment page.
        """
        form = UploadTXTForm(request.POST, request.FILES)
        if form.is_valid():
            # safe file if form is valid
            safeFile(request, form, "txtFile", "transscript")
        else:
            print("invalid form")
            print(form.errors)
            # return error to AJAX function to print
        return HttpResponseRedirect("/accounts/overview/")
