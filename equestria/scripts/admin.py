"""Module to register thing to be available in admin page."""
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from scripts import models
from .forms import ChoiceParameterAdminForm
from nested_inline.admin import NestedStackedInline, NestedModelAdmin
from django import forms
from django.contrib import messages


class BooleanParameterInline(NestedStackedInline):
    """Display BooleanParameter objects inline."""

    model = models.BooleanParameter
    extra = 0


class StaticParameterInline(NestedStackedInline):
    """Display StaticParameter objects inline."""

    model = models.StaticParameter
    extra = 0


class StringParameterInline(NestedStackedInline):
    """Display StringParameter objects inline."""

    model = models.StringParameter
    extra = 0


class ChoiceInline(NestedStackedInline):
    """Display Choice objects inline."""

    model = models.Choice
    extra = 0
    fk_name = "corresponding_choice_parameter"


class ChoiceParameterInline(NestedStackedInline):
    """Display ChoiceParameter objects inline."""

    form = ChoiceParameterAdminForm

    model = models.ChoiceParameter
    extra = 0


class TextParameterInline(NestedStackedInline):
    """Display TextParameter objects inline."""

    model = models.TextParameter
    extra = 0


class IntegerParameterInline(NestedStackedInline):
    """Display IntegerParameter objects inline."""

    model = models.IntegerParameter
    extra = 0


class FloatParameterInline(NestedStackedInline):
    """Display FloatParameter objects inline."""

    model = models.FloatParameter
    extra = 0


class ChoiceParameterAdmin(NestedModelAdmin):
    """Admin screen for showing choices inline."""

    form = ChoiceParameterAdminForm

    inlines = [ChoiceInline]


class ProfileInline(NestedStackedInline):
    """
    Display profiles as a stacked inline form in the admin panel.

    Show only profile objects that are explicitly created, do not show empty ones.
    """

    model = models.Profile
    extra = 0


class BaseParameterInline(admin.StackedInline):
    """Display BaseParameter objects inline."""

    model = models.BaseParameter
    extra = 0

    exclude = ["name", "type", "preset"]


class ScriptAdmin(NestedModelAdmin):
    """Profiles are displayed inline when creating/modifying processes."""

    inlines = [ProfileInline, BaseParameterInline]

    def change_view(self, request, object_id, form_url="", extra_context=None):
        """
        Add a show_refresh to the context.

        :param request: the request
        :param object_id: object id
        :param form_url: form url
        :param extra_context: extra content
        :return: changeform_view with added context
        """
        try:
            extra_context["show_refresh"] = True
        except TypeError:
            extra_context = {"show_refresh": True}
        return self.changeform_view(request, object_id, form_url, extra_context)

    def response_change(self, request, obj):
        """
        Add refresh functionality to the django script admin.

        :param request: the request
        :param obj: object
        :return: the super method of response_change if refresh is not set, otherwise refreshes the script and redirects
        to the same page with a success or error message.
        """
        if "_refresh" in request.POST:
            try:
                obj.refresh()
                self.message_user(request, "CLAM data refreshed successfully")
            except ValidationError as e:
                self.message_user(
                    request, e.message, level=messages.ERROR,
                )
            return HttpResponseRedirect(".")
        return super().response_change(request, obj)


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
    """Admin screen for showing parameters inline."""

    inlines = [
        BooleanParameterInline,
        StaticParameterInline,
        StringParameterInline,
        ChoiceParameterInline,
        TextParameterInline,
        IntegerParameterInline,
        FloatParameterInline,
    ]


admin.site.register(models.Script, ScriptAdmin)
admin.site.register(models.Process)
admin.site.register(models.Project)
admin.site.register(models.Pipeline)
admin.site.register(models.InputTemplate)
admin.site.register(models.Profile, ProfileAdmin)
admin.site.register(models.BaseParameter, ParameterAdmin)
admin.site.register(models.ChoiceParameter, ChoiceParameterAdmin)
