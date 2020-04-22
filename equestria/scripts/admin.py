"""Module to register thing to be available in admin page."""
from django.contrib import admin
from scripts import models

# Register your models here.


class ProfileInline(admin.StackedInline):
    """
    Display profiles as a stacked inline form in the admin panel.

    Show only profile objects that are explicitly created, do not show empty ones.
    """

    model = models.Profile
    extra = 0


class ScriptAdmin(admin.ModelAdmin):
    """Profiles are displayed inline when creating/modifying processes."""

    inlines = [ProfileInline]


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


admin.site.register(models.Script, ScriptAdmin)
admin.site.register(models.Process)
admin.site.register(models.Project)
admin.site.register(models.Pipeline)
admin.site.register(models.InputTemplate)
admin.site.register(models.Profile, ProfileAdmin)
