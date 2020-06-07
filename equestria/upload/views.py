"""Module to handle uploading files."""
import os
from django.http import Http404
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from scripts.models import InputTemplate, Project, Profile

from .forms import UploadForm
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.mixins import LoginRequiredMixin
import zipfile
import shutil
from django.core.exceptions import PermissionDenied


class UploadProjectView(LoginRequiredMixin, TemplateView):
    """View for initial upload of files to a project."""

    login_url = "/accounts/login/"

    template_name = "upload/upload-project.html"

    def get_standard_context(self, project):
        """
        Get the standard context for rendering this view.

        :param project: the project to render the view for
        :return: a context attribute with standard context for the view
        """
        files = [
            x
            for x in os.listdir(project.folder)
            if os.path.isfile(os.path.join(project.folder, x))
        ]
        templates = InputTemplate.objects.filter(
            corresponding_profile__script=project.pipeline.fa_script
        )
        extensions = list(set([x.extension for x in templates]))
        context = {
            "project": project,
            "files": files,
            "extensions": extensions,
            "profiles": Profile.objects.filter(
                script=project.pipeline.fa_script
            ),
        }
        if project.can_start_new_process():
            context["can_start"] = True
        return context

    def get(self, request, **kwargs):
        """
        Handle a GET request for the file upload page.

        :param request: the request
        :param kwargs: keyword arguments
        :return: A render of the upload_project.html page containing an upload form if files can be uploaded to the
        project and a profile form if a new process can be started for the project
        """
        project = kwargs.get("project")
        if not request.user.has_perm("access_project", project):
            raise PermissionDenied
        context = self.get_standard_context(project)
        if project.can_upload():
            context["upload_form"] = UploadForm()
        return render(request, self.template_name, context)

    def post(self, request, **kwargs):
        """
        Upload file view for uploading a file from a form.

        :param request: the request
        :param kwargs: keyword arguments
        :return: a redirect if the file upload succeeded, raises a StateException if the file can't be uploaded because the
        project has a running process
        """
        project = kwargs.get("project")
        if not request.user.has_perm("access_project", project):
            raise PermissionDenied

        if not project.can_upload():
            raise Http404("Can't upload files to this project")

        templates = InputTemplate.objects.filter(
            corresponding_profile__script=project.pipeline.fa_script
        )
        extensions = [x.extension for x in templates]

        upload_form = UploadForm(request.POST, request.FILES)
        non_saved = list()
        if upload_form.is_valid():
            uploaded_files = request.FILES.getlist("f")
            for file in uploaded_files:
                name, extension = os.path.splitext(file.name)
                if extension[1:] == "zip":
                    non_saved += save_zipped_files(project, file)
                elif extension[1:] in extensions:
                    save_file(project, file)
                else:
                    non_saved.append(file)
            context = self.get_standard_context(project)
            context["upload_form"] = UploadForm()
            context["removed_list"] = non_saved
            return render(request, self.template_name, context)
        else:
            context = self.get_standard_context(project)
            context["upload_form"] = upload_form
            return render(request, self.template_name, context)


def handle_folders(project):
    """
    Handle folders in the project folder if they are uploaded.

    :param request: the project
    :return: None
    """
    subdirs = [x[0] for x in os.walk(project.folder)]
    subdirs.pop(0)
    subdirs.reverse()
    for sd in subdirs:
        for file in os.listdir(sd):
            full_path = os.path.join(sd, file)
            if os.path.isfile(full_path):
                file_in_root = os.path.join(project.folder, file)
                if os.path.isfile(file_in_root):
                    os.remove(file_in_root)
                shutil.move(full_path, project.folder)
        shutil.rmtree(sd)


def save_zipped_files(project, file):
    """
    Save zipped files to a project.

    :param project: the project to save the file to
    :param file: the zip file of type <class 'django.core.files.uploadedfile.InMemoryUploadedFile'>
    :return: None
    """
    templates = InputTemplate.objects.filter(
        corresponding_profile__script=project.pipeline.fa_script
    )
    extensions = [x.extension for x in templates]
    with zipfile.ZipFile(file) as zip_file:
        zip_file.extractall(
            os.path.join(project.folder, Project.EXTRACT_FOLDER)
        )

    non_copied = project.move_extracted_files(extensions)
    shutil.rmtree(os.path.join(project.folder, Project.EXTRACT_FOLDER))
    return non_copied


def save_file(project, file):
    """
    Save a file to a project.
    
    :param project: the project to save the file to
    :param file: the file to be uploaded
    :return: None
    """
    path = project.folder
    fs = FileSystemStorage(location=path)
    if fs.exists(file.name):
        """Delete previously uploaded file with same name."""
        fs.delete(file.name)
    fs.save(file.name, file)


def delete_file_view(request, **kwargs):
    """
    Delete file view for deleting a file.

    :param request: the request
    :param kwargs: keyword arguments
    :return: a redirect if the file deletion succeeded, raises a StateException if the file can't be deleted because the
    file does not exist
    """
    project = kwargs.get("project")
    file = request.POST.get("file")
    if os.path.exists(os.path.join(project.folder, file)):
        os.remove(os.path.join(project.folder, file))
        return redirect("upload:upload_project", project=project)
    else:
        raise Http404("File does not exist")
