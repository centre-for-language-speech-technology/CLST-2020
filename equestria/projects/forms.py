"""Module to define forms related to the scripts app."""
from django import forms
from django.core.validators import RegexValidator
from pipelines.models import Pipeline

from .models import Project, File

alphanumeric = RegexValidator(
    r"^[0-9a-zA-Z]*$", "Only alphanumeric characters are allowed."
)


class ProjectCreateForm(forms.Form):
    """Form for project creation."""

    project_name = forms.CharField(
        label="Project name", required=True, validators=[alphanumeric]
    )
    pipeline = forms.ChoiceField(choices=[])

    def __init__(self, user, *args, **kwargs):
        """
        Initialise method for ProjectCreateForm.

        :param args: argument
        :param kwargs: keyword arguments containing a scripts variable with Script objects
        """
        self.user = user
        pipelines = kwargs.pop("pipelines", None)
        super(ProjectCreateForm, self).__init__(*args, **kwargs)
        choices = []
        if pipelines is not None:
            for pipeline in pipelines:
                choices.append((pipeline.id, pipeline.name))
            self.fields["pipeline"].choices = choices

    def clean_project_name(self):
        """
        Clean the project name in this form.

        :return: the cleaned project name
        """
        project_name = self.cleaned_data.get("project_name")

        project_qs = Project.objects.filter(name=project_name, user=self.user)
        if project_qs.exists():
            raise forms.ValidationError("This project does already exist")

        return project_name

    def clean_pipeline(self):
        """
        Clean the script variable in this form.

        :return: the cleaned script variable
        """
        pipeline = self.cleaned_data.get("pipeline")
        pipeline_qs = Pipeline.objects.filter(id=pipeline)
        if not pipeline_qs.exists():
            raise forms.ValidationError("This pipeline does not exist")

        return pipeline


class UploadForm(forms.ModelForm):
    """Form to upload file."""

    class Meta:
        """Meta class."""

        model = File
        fields = ["file"]
