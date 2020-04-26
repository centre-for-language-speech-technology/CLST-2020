"""Module to define forms related to the scripts app."""
from django import forms
from django.contrib.auth import get_user_model
from .models import Project, Pipeline, Profile, BaseParameter
from django.core.validators import RegexValidator
from .models import ChoiceParameter, Choice

alphanumeric = RegexValidator(
    r"^[0-9a-zA-Z]*$", "Only alphanumeric characters are allowed."
)

User = get_user_model()


class ProfileSelectForm(forms.Form):
    """Form for running a profile."""

    profile = forms.ChoiceField(choices=[])

    def __init__(self, *args, **kwargs):
        """
        Initialise method for ProfileSelectForm.

        :param args: argument
        :param kwargs: keyword arguments containing a scripts variable with Script objects
        """
        profiles = kwargs.pop("profiles", None)
        super(ProfileSelectForm, self).__init__(*args, **kwargs)
        choices = []
        if profiles is not None:
            for p in profiles:
                choices.append((p.id, "Profile {}".format(p.id)))
            self.fields["profile"].choices = choices

    def clean_profile(self):
        """
        Clean the profile variable in this form.

        :return: the cleaned profile variable
        """
        profile = self.cleaned_data.get("profile")
        profile_qs = Profile.objects.filter(id=profile)
        if not profile_qs.exists():
            raise forms.ValidationError("This profile does not exist")

        return profile


class AlterDictionaryForm(forms.Form):
    """Form for altering the dictionary."""

    dictionary = forms.CharField(
        widget=forms.Textarea(attrs={"style": "width: 100%;"}),
        required=False,
        label=False,
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


class ParameterForm(forms.Form):
    """Form for setting parameters."""

    def __init__(self, parameters, *args, **kwargs):
        """
        Initialise the ParameterForm.

        :param parameters: a list of BaseParameter objects including the parameters to add to this form, field types are
        automatically set for the parameters
        :param args: arguments
        :param kwargs: keyword arguments
        """
        super(ParameterForm, self).__init__(*args, **kwargs)
        for parameter in parameters:
            if parameter.type == BaseParameter.BOOLEAN_TYPE:
                self.fields[parameter.name] = forms.BooleanField()
            elif parameter.type == BaseParameter.STATIC_TYPE:
                self.fields[parameter.name] = forms.CharField(
                    widget=forms.HiddenInput(),
                    initial=parameter.get_default_value(),
                )
            elif parameter.type == BaseParameter.STRING_TYPE:
                self.fields[parameter.name] = forms.CharField()
            elif parameter.type == BaseParameter.CHOICE_TYPE:
                self.fields[parameter.name] = forms.ChoiceField(choices=[])
                choice_parameter = ChoiceParameter.objects.get(base=parameter)
                choices = list()
                for choice in Choice.objects.filter(
                    corresponding_choice_parameter=choice_parameter
                ):
                    choices.append((choice.id, choice.value))
                self.fields[parameter.name].choices = choices
            elif parameter.type == BaseParameter.TEXT_TYPE:
                self.fields[parameter.name] = forms.CharField(
                    widget=forms.Textarea
                )
            elif parameter.type == BaseParameter.INTEGER_TYPE:
                self.fields[parameter.name] = forms.IntegerField()
            elif parameter.type == BaseParameter.FLOAT_TYPE:
                self.fields[parameter.name] = forms.FloatField()


class ChoiceParameterAdminForm(forms.ModelForm):
    """Admin form for ChoiceParameter."""

    class Meta:
        """Meta class."""

        model = ChoiceParameter
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        """
        Initialise the ChoiceParameterAdminForm.

        This method restricts the choices on the 'value' field in the admin form to choices that correspond to the
        ChoiceParameter object.
        :param args: arguments
        :param kwargs: keyword arguments
        """
        super(ChoiceParameterAdminForm, self).__init__(*args, **kwargs)
        if self.instance:
            self.fields["value"].queryset = Choice.objects.filter(
                corresponding_choice_parameter=self.instance
            )
