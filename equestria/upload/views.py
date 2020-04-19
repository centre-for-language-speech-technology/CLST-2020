"""Module to handle uploading files."""
import os
from django.conf import settings
from scripts.models import Project, Profile, InputTemplate
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from .models import File
from .forms import UploadForm
from scripts.forms import ProfileSelectForm
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.mixins import LoginRequiredMixin
import mimetypes


class UploadProjectView(LoginRequiredMixin, TemplateView):
    """View for initial upload of files to a project."""

    login_url = "/accounts/login/"
    redirect_field_name = "redirect_to"
    template_name = "upload/upload-project.html"

    def getValidProfiles(self, request, p_id):
        """Get profiles for which the current files meet the requirements."""
        profiles = Profile.objects.all()
        validProfiles = []

        for p in profiles:
            if p.is_valid(
                os.path.join(
                    settings.USER_DATA_FOLDER,
                    request.user.username,
                    Project.objects.get(id=p_id).name,
                )
            ):
                validProfiles.append(p)
        return validProfiles

    def makeProfileForm(self, request, p_id):
        """Make a profile form to be used in this class."""
        validProfiles = self.getValidProfiles(request, p_id)
        return ProfileSelectForm(
            request.user, request.POST, profiles=validProfiles
        )

    def get(self, request, **kwargs):
        """Handle GET requests file upload apge."""
        p_id = kwargs.get("project_id")

        files = File.objects.filter(owner=request.user.username, project=p_id)
        profileForm = self.makeProfileForm(request, p_id)

        uploadForm = UploadForm()
        uploadForm.p_id = p_id
        context = {
            "files": files,
            "UploadForm": uploadForm,
            "ProfileForm": profileForm,
        }
        return render(request, self.template_name, context)

    def post(self, request, **kwargs):
        """Handle POST requests file upload page."""
        form = UploadForm(request.POST, request.FILES)
        p_id = kwargs.get("project_id")

        if form.is_valid():
            safeFile(request, form, p_id)
        else:
            prof_id = request.POST.get("profiles")

            return redirect(
                "scripts:fa_start", project_id=p_id, profile_id=prof_id
            )

        files = File.objects.filter(owner=request.user.username, project=p_id)

        profileForm = self.makeProfileForm(request, p_id)

        uploadForm = UploadForm()
        uploadForm.p_id = p_id
        context = {
            "files": files,
            "UploadForm": uploadForm,
            "ProfileForm": profileForm,
        }
        return render(request, self.template_name, context)


def getFileType(path):
    """Get the file type of the uploaded file and categorize."""
    mime = mimetypes.guess_type(path)
    return mime[0]


def makeDBEntry(request, path, useFor, p_id):
    """Create an entry in the Database for the uploaded file."""
    exists = File.objects.filter(path=path)
    if len(exists) > 0:
        exists[0].delete()
    file = File()
    file.owner = request.user.username
    file.path = path
    file.project = p_id
    file.filetype = getFileType(path)
    file.usage = useFor
    file.save()


def safeFile(request, form, p_id):
    """Safe uploaded file."""
    username = request.user.username
    uploadedfile = request.FILES["f"]
    project = Project.objects.get(id=p_id).name
    path = os.path.join("userdata", username, project)
    absolutePath = os.path.join(
        settings.USER_DATA_FOLDER, username, project, uploadedfile.name
    )
    fs = FileSystemStorage(location=path)

    if fs.exists(uploadedfile.name):
        """Delete previously uploaded file with same name."""
        os.remove(absolutePath)

    ext = uploadedfile.name.split(".")[-1]
    if ext == "txt" or ext == "tg":
        useFor = "text"
    else:
        useFor = "audio"

    makeDBEntry(request, absolutePath, useFor, p_id)
    fs.save(uploadedfile.name, uploadedfile)
