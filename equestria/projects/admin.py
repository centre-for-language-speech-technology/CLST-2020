from django.contrib import admin
from projects import models


@admin.register(models.Project)
class ProjectAdmin(admin.ModelAdmin):
    """Model admin for Projects."""

    list_display = ["name", "user", "pipeline"]
    list_filter = ["user", "pipeline"]


@admin.register(models.File)
class FileAdmin(admin.ModelAdmin):
    """Model admin for Files."""

    list_display = ["__str__", "project"]
    list_filter = ["project"]
