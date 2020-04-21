"""Module to handle uploading files."""
import os
from scripts.models import Profile, Project
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

    template_name = "upload/upload-project.html"

    def get(self, request, **kwargs):
        """
        Handle a GET request for the file upload page.

        :param request: the request
        :param kwargs: keyword arguments
        :return: A render of the upload_project.html page containing an upload form if files can be uploaded to the
        project and a profile form if a new process can be started for the project
        """
        project = kwargs.get("project")
        files = File.objects.filter(
            owner=request.user.username, project=project
        )
        context = {
            "project": project,
            "files": files,
        }
        if project.can_upload():
            context["upload_form"] = UploadForm()
        if project.can_start_new_process():
            valid_profiles = project.pipeline.fa_script.get_valid_profiles(
                project.folder
            )
            context["profile_form"] = ProfileSelectForm(profiles=valid_profiles)
        return render(request, self.template_name, context)

    def post(self, request, **kwargs):
        """
        Handle POST request for file upload page.

        :param request: the request
        :param kwargs: keyword arguments
        :return: a ValueError if the profile in the form is not valid, a render of the upload_project.html page if there
        is already a started process, a redirect to the fa_start view otherwise
        """
        project = kwargs.get("project")
        if not project.can_start_new_process():
            return self.get(request, **kwargs)

        valid_profiles = project.pipeline.fa_script.get_valid_profiles(
            project.folder
        )
        profile_form = ProfileSelectForm(request.POST, profiles=valid_profiles)

        if profile_form.is_valid():
            return redirect(
                "scripts:fa_start",
                project=project,
                profile=Profile.objects.get(
                    pk=profile_form.cleaned_data.get("profile")
                ),
            )
        else:
            raise ValueError("Profile form is invalid.")


def upload_file_view(request, **kwargs):
    """
    Upload file view for uploading a file from a form.

    :param request: the request
    :param kwargs: keyword arguments
    :return: a redirect if the file upload succeeded, raises a StateException if the file can't be uploaded because the
    project has a running process, raises a ValueError if the form is not valid
    """
    project = kwargs.get("project")
    if not project.can_upload():
        raise Project.StateException("Can't upload files to this project")
    upload_form = UploadForm(request.POST, request.FILES)

    if upload_form.is_valid():
        save_file(request, project)
        return redirect("upload:upload_project", project=project)
    else:
        raise ValueError("File upload form invalid.")


def get_file_type(path):
    """
    Get the file type of the uploaded file.

    :param path: the path of the file
    :return: the filetype
    """
    mime = mimetypes.guess_type(path)
    return mime[0]


def make_db_entry(request, path, use_for, project):
    """
    Create a database entry for an uploaded file.

    :param request: the request
    :param path: the path of the file
    :param use_for: what to use the file for, either text or audio
    :param project: the project the file belongs to
    :return: None
    """
    exists = File.objects.filter(path=path)
    if len(exists) > 0:
        exists[0].delete()
    file = File()
    file.owner = request.user.username
    file.path = path
    file.project = project
    file.filetype = get_file_type(path)
    file.usage = use_for
    file.save()


def save_file(request, project):
    """
    Save a file to a project.

    :param request: the request
    :param project: the project to save the file to
    :return: None
    """
    uploaded_file = request.FILES["f"]
    path = project.folder
    save_location = os.path.join(path, uploaded_file.name)
    fs = FileSystemStorage(location=path)

    if fs.exists(uploaded_file.name):
        """Delete previously uploaded file with same name."""
        os.remove(save_location)

    ext = uploaded_file.name.split(".")[-1]
    if ext == "txt" or ext == "tg":
        use_for = "text"
    else:
        use_for = "audio"

    make_db_entry(request, save_location, use_for, project)
    fs.save(uploaded_file.name, uploaded_file)
