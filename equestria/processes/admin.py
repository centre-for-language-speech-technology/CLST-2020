from django.contrib import admin
from processes import models
from processes.forms import FilePresetAdminForm, PreferableFileAdminForm


class FileDisplayRegexInline(admin.StackedInline):
    """Display File Regex objects inline."""

    model = models.PreferableFile
    form = PreferableFileAdminForm
    extra = 0

    include = ["regex"]


class FilePresetInline(admin.StackedInline):
    """Display File Preset objects inline."""

    model = models.FilePreset
    form = FilePresetAdminForm
    extra = 0

    include = ["regex"]


@admin.register(models.Process)
class ProcessAdmin(admin.ModelAdmin):
    """Model admin for Processes."""

    list_display = ["id", "project", "script", "status"]
    list_filter = ["status", "script", "project"]
