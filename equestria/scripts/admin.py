"""Module to register thing to be available in admin page."""
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.safestring import mark_safe
from scripts import models
from .forms import ChoiceParameterAdminForm
from nested_inline.admin import NestedStackedInline, NestedModelAdmin
from django.contrib import messages
from scripts.forms import OutputTemplateAdminForm
from processes.admin import FileDisplayRegexInline, FilePresetInline


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


@admin.register(models.ChoiceParameter)
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
    readonly_fields = ("admin_page",)
    exclude = ["name"]

    def admin_page(self, obj):
        """Get a link to the admin page."""
        if obj.id is None:
            return mark_safe(
                '<a class="disabled">Can not edit, please save model first</a>'
            )
        return mark_safe(
            '<a href="{}">Click to edit</a>'.format(
                reverse("admin:scripts_profile_change", args=(obj.id,))
            )
        )


class BaseParameterInline(admin.StackedInline):
    """Display BaseParameter objects inline."""

    model = models.BaseParameter
    extra = 0
    inlines = []
    readonly_fields = ("admin_page",)
    exclude = ["name", "preset", "type"]

    def admin_page(self, obj):
        """Get a link to the admin page."""
        if obj.id is None:
            return mark_safe(
                '<a class="disabled">Can not edit, please save model first</a>'
            )
        return mark_safe(
            '<a href="{}">Click to edit</a>'.format(
                reverse("admin:scripts_baseparameter_change", args=(obj.id,))
            )
        )


class OutputTemplateInline(admin.StackedInline):
    """Inline for OutputTemplates."""

    form = OutputTemplateAdminForm
    model = models.OutputTemplate
    inlines = []
    extra = 0

    include = ["regex"]


@admin.register(models.Script)
class ScriptAdmin(NestedModelAdmin):
    """Profiles are displayed inline when creating/modifying processes."""

    inlines = [ProfileInline, BaseParameterInline, OutputTemplateInline]

    list_display = ["name", "hostname"]

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
    inlines = []
    extra = 0


@admin.register(models.Profile)
class ProfileAdmin(admin.ModelAdmin):
    """Input templates are displayed inline when creating/modifying profiles."""

    inlines = [InputTemplateInline]
    list_display = ["__str__", "script"]
    list_filter = ["script"]


@admin.register(models.BaseParameter)
class ParameterAdmin(NestedModelAdmin):
    """Admin screen for showing parameters inline."""

    list_display = ["name", "corresponding_script"]
    list_filter = ["name", "corresponding_script"]

    inlines = [
        BooleanParameterInline,
        StaticParameterInline,
        StringParameterInline,
        ChoiceParameterInline,
        TextParameterInline,
        IntegerParameterInline,
        FloatParameterInline,
    ]


@admin.register(models.InputTemplate)
class InputTemplateAdmin(admin.ModelAdmin):
    """Model admin for InputTemplates."""

    list_display = [
        "template_id",
        "extension",
        "corresponding_profile",
        "optional",
        "unique",
    ]
    inlines = [FileDisplayRegexInline, FilePresetInline]
    list_filter = ["corresponding_profile", "extension"]
