from django.contrib import admin
from script_runner import models

# Register your models here.


class ArgumentInline(admin.StackedInline):
    """
    Display Arguments as a stacked inline form in the admin panel.

    Show only arguments that are explicitly created, do not show empty ones.
    """

    model = models.Argument
    extra = 0


class OutputFileInline(admin.StackedInline):
    """
    Display output files as a stacked inline form in the admin panel.

    Show only output file objects that are explicitly created, do not show empty ones.
    """

    model = models.OutputFile
    extra = 0


class ScriptAdmin(admin.ModelAdmin):
    """Arguments and ouput files are displayed inline when creating/modifying scripts."""

    inlines = [
        ArgumentInline,
        OutputFileInline,
    ]


class ProfileInline(admin.StackedInline):
    model = models.Profile
    extra = 0


class ProcessAdmin(admin.ModelAdmin):
    """Process does not have inline fields (but may get them later)."""

    inlines = [
        ProfileInline
    ]


class InputTemplateInline(admin.StackedInline):
    model = models.InputTemplate
    extra = 0


class ProfileAdmin(admin.ModelAdmin):
    inlines = [
        InputTemplateInline
    ]

admin.site.register(models.Script, ScriptAdmin)
admin.site.register(models.Process, ProcessAdmin)
admin.site.register(models.Profile, ProfileAdmin)