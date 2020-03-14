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


admin.site.register(models.Script, ScriptAdmin)
