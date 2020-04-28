"""Module to handle uploading files."""
import os
from django.http import Http404
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from .models import File
from .forms import UploadForm
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.mixins import LoginRequiredMixin
import mimetypes
from django.core.exceptions import ValidationError
import zipfile


class UploadProjectView(LoginRequiredMixin, TemplateView):
    """View for initial upload of files to a project."""

    login_url = "/accounts/login/"

    template_name = "upload-project.html"

    def get(self, request, **kwargs):
        """
        Handle a GET request for the file upload page.

        :param request: the request
        :param kwargs: keyword arguments
        :return: A render of the upload_project.html page containing an upload form if files can be uploaded to the
        project and a profile form if a new process can be started for the project
        """
        project = kwargs.get("project")
        files = os.listdir(project.folder)
        context = {
            "project": project,
            "files": files,
        }
        if project.can_upload():
            context["upload_form"] = UploadForm()
        if project.can_start_new_process():
            context["can_start"] = True
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

        return redirect("scripts:fa_start_automatic", project=project)


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
        raise Http404("Can't upload files to this project")
    upload_form = UploadForm(request.POST, request.FILES)

    if upload_form.is_valid():
        uploaded_files = request.FILES.getlist("f")
        for file in uploaded_files:
            ext = file.name.split(".")[-1]
            if ext == "zip":
                save_zipped_files(request, project, file)
            elif ext in ["wav", "txt", "tg"]:
                save_file(request, project, file)
    return redirect("upload:upload_project", project=project)


def save_zipped_files(request, project, file):
    """
    Save zipped files to a project.

    :param request: the request
    :param project: the project to save the file to
    :param file: the zip file
    :return: None
    """

    path = project.folder
    save_location = os.path.join(path, file.name)
    fs = FileSystemStorage(location=path)

    if fs.exists(file.name):
        """Delete previously uploaded file with same name."""
        os.remove(save_location)

    with zipfile.ZipFile(file) as zip_file:
        names = zip_file.namelist()
        for name in names:
            with zip_file.open(name) as f:
                ext = name.split(".")[-1]

                if ext == "zip":
                    """Zip in a zip"""
                    save_zipped_files(request, project, f)
                elif ext in ["wav", "txt", "tg"]:
                    save_file(request, project, f)


def save_file(request, project, file):
    """
    Save a file to a project.

    :param request: the request
    :param project: the project to save the file to
    :param file: the file to be uploaded
    :return: None
    """

    path = project.folder
    save_location = os.path.join(path, file.name)
    fs = FileSystemStorage(location=path)

    if fs.exists(file.name):
        """Delete previously uploaded file with same name."""
        os.remove(save_location)

    ext = file.name.split(".")[-1]
    if ext == "txt" or ext == "tg":
        use_for = "text"
    elif ext == "wav":
        use_for = "audio"
    else:
        raise ValidationError("Unsupported file extension.")

    fs.save(file.name, file)
