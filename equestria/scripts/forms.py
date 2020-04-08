from django import forms
from django.contrib.auth import get_user_model
from .models import Process, Script

User = get_user_model()


class ProjectCreateForm(forms.Form):
    """Form for project creation."""

    project_name = forms.CharField(label="Project name", required=True)
    script = forms.ChoiceField(choices=[])

    def __init__(self, *args, **kwargs):
        """
        Initialise method for ProjectCreateForm.

        :param args: argument
        :param kwargs: keyword arguments containing a scripts variable with Script objects
        """
        scripts = kwargs.pop("scripts", None)
        super(ProjectCreateForm, self).__init__(*args, **kwargs)
        choices = []
        if scripts is not None:
            for script in scripts:
                choices.append((script.id, script.name))
            self.fields["script"].choices = choices

    def clean_project_name(self):
        """
        Clean the project name in this form.

        :return: the cleaned project name
        """
        project_name = self.cleaned_data.get("project_name")

        project_qs = Process.objects.filter(name=project_name)
        if project_qs.exists():
            raise forms.ValidationError("This project does already exist")

        return project_name

    def clean_script(self):
        """
        Clean the script variable in this form.

        :return: the cleaned script variable
        """
        script = self.cleaned_data.get("script")
        script_qs = Script.objects.filter(id=script)
        if not script_qs.exists():
            raise forms.ValidationError("This script does not exist")

        return script
