import os
from django.conf import settings
from scripts.models import Project
from django.shortcuts import render
from django.views.generic import TemplateView
from .models import File
from .forms import UploadForm, UploadWAVForm
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
import mimetypes

"""Module to handle uploading files."""


class UploadProjectView(LoginRequiredMixin, TemplateView):
    """View for initial upload of files to a project."""

    login_url = "/accounts/login/"
    redirect_field_name = "redirect_to"
    template_name = "upload/upload-project.html"

    def get(self, request, **kwargs):
        """Display files."""
        files = File.objects.filter(owner=request.user.username)
        txtForm = UploadForm()
        txtForm.p_id =  kwargs.get("project_id")
        context = {
            "files": files,
            "TXTform": txtForm,
        }
        return render(request, self.template_name, context)

    def post(self, request, **kwargs):
        """Handle POST requests to upload/wav.

        Also acts as callback function from forced alignment page.
        """
        form = UploadForm(request.POST, request.FILES)
        #print(kwargs.get("project_id"))
        if form.is_valid():
            safeFile(request, form, kwargs.get("project_id"))
        else:
            print("invalid form")
            print(form.errors)
            # return error to AJAX function to print
        files = File.objects.filter(owner=request.user.username)
        txtForm = UploadForm()
        txtForm.p_id =  kwargs.get("project_id")
        context = {
            "files": files,
            "TXTform": txtForm,
        }
        return render(request, self.template_name, context)


def getFileType(path):
    """Get the file type of the uploaded file and categorize."""
    mime = mimetypes.guess_type(path)
    return mime[0]


def makeDBEntry(request, path, useFor):
    """Create an entry in the Database for the uploaded file."""
    exists = File.objects.filter(path = path)
    if (len(exists) > 0):
        exists[0].delete()
    file = File()
    file.owner = request.user.username
    file.path = path
    file.filetype = getFileType(path)
    file.usage = useFor
    file.save()


def safeFile(request, form, p_id):
    """Safe uploaded file."""
    username = request.user.username
    uploadedfile = request.FILES['f']
    project = Project.objects.get(id=p_id).name
    path = os.path.join("userdata", username, project)
    absolutePath = os.path.join(
        settings.USER_DATA_FOLDER, username, project, uploadedfile.name
    )
    fs = FileSystemStorage(location=path)

    if fs.exists(uploadedfile.name):
        """Delete previously uploaded file with same name."""
        os.remove(absolutePath)

    ext = uploadedfile.name.split('.')[-1]
    if (ext == 'txt' or ext == 'tg'):
        useFor = 'text'
    else:
        useFor = 'audio'

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
        return HttpResponseRedirect(request.resolver_match.url_name)


class UploadTXTView(LoginRequiredMixin, TemplateView):
    """Handle the upload/txt page.

    Also acts as callback URL for the uploads in forced alignment page.
    """

    login_url = "/accounts/login/"
    redirect_field_name = "redirect_to"

    template_name = "upload_txt2.html"


    def get(self, request):
        """Handle GET requests to upload/txt."""
        form = UploadForm()
        form.p_id = ''
        return render(request, self.template_name, {"TXTform": form})

    def post(self, request):
        """Handle POST requests to upload/txt.

        Also acts as callback function from forced alignment page.
        """
        form = UploadForm(request.POST, request.FILES)
        callback_url = form['callback_url'].value()
        p_id = form.data['p_id']
        if form.is_valid():
            # safe file if form is valid
            safeFile(request, form, "txtFile", "transscript")
        else:
            print("invalid form")
            print(form.errors)
            # return error to AJAX function to print
        return HttpResponseRedirect(callback_url)
