from django.contrib import admin
from pipelines import models
from pipelines.forms import DictionaryFileFormatAdminForm


class DictionaryFileFormatInline(admin.StackedInline):
    """Dictionary File Format Inline."""

    model = models.DictionaryFileFormat
    form = DictionaryFileFormatAdminForm
    extra = 0

    include = ["regex"]


@admin.register(models.Pipeline)
class PipelineAdmin(admin.ModelAdmin):
    """Model admin for Pipelines."""

    list_display = ["name", "fa_script", "g2p_script"]
    inlines = [DictionaryFileFormatInline]
