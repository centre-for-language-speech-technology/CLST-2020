"""Module to register thing to be available in admin page."""
from django.contrib import admin
from scripts import models
from .forms import ChoiceParameterAdminForm
from nested_inline.admin import NestedStackedInline, NestedModelAdmin


class BooleanParameterInline(NestedStackedInline):

    model = models.BooleanParameter
    extra = 0


class StaticParameterInline(NestedStackedInline):

    model = models.StaticParameter
    extra = 0


class StringParameterInline(NestedStackedInline):

    model = models.StringParameter
    extra = 0


class ChoiceInline(NestedStackedInline):

    model = models.Choice
    extra = 0
    fk_name = "corresponding_choice_parameter"


class ChoiceParameterInline(NestedStackedInline):

    form = ChoiceParameterAdminForm

    model = models.ChoiceParameter
    extra = 0


class TextParameterInline(NestedStackedInline):

    model = models.TextParameter
    extra = 0


class IntegerParameterInline(NestedStackedInline):

    model = models.IntegerParameter
    extra = 0


class FloatParameterInline(NestedStackedInline):

    model = models.FloatParameter
    extra = 0


class ChoiceParameterAdmin(NestedModelAdmin):

    form = ChoiceParameterAdminForm

    inlines = [
        ChoiceInline
    ]


class ProfileInline(NestedStackedInline):
    """
    Display profiles as a stacked inline form in the admin panel.

    Show only profile objects that are explicitly created, do not show empty ones.
    """

    model = models.Profile
    extra = 0


class BaseParameterInline(admin.StackedInline):

    model = models.BaseParameter
    extra = 0

    exclude = ['name', 'type', 'preset']


class ScriptAdmin(NestedModelAdmin):
    """Profiles are displayed inline when creating/modifying processes."""

    inlines = [
        ProfileInline,
        BaseParameterInline
    ]


class InputTemplateInline(admin.StackedInline):
    """
    Display input templates as a stacked inline form in the admin panel.

    Show only input template objects that are explicitly created, do not show empty ones.
    """

    model = models.InputTemplate
    extra = 0


class ProfileAdmin(admin.ModelAdmin):
    """Input templates are displayed inline when creating/modifying profiles."""

    inlines = [InputTemplateInline]


class ParameterAdmin(NestedModelAdmin):

    inlines = [
        BooleanParameterInline,
        StaticParameterInline,
        StringParameterInline,
        ChoiceParameterInline,
        TextParameterInline,
        IntegerParameterInline,
        FloatParameterInline
    ]


admin.site.register(models.Script, ScriptAdmin)
admin.site.register(models.Process)
admin.site.register(models.Project)
admin.site.register(models.Pipeline)
admin.site.register(models.InputTemplate)
admin.site.register(models.Profile, ProfileAdmin)
admin.site.register(models.BaseParameter, ParameterAdmin)
admin.site.register(models.ChoiceParameter, ChoiceParameterAdmin)
