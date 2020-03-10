from django.contrib import admin
from script_runner import models

# Register your models here.


class ArgumentInline(admin.StackedInline):
    model = models.Argument
    extra = 0


class OutputFileInline(admin.StackedInline):
    model = models.OutputFile
    extra = 0


class ScriptAdmin(admin.ModelAdmin):
    inlines = [
        ArgumentInline,
        OutputFileInline,
    ]


admin.site.register(models.Script, ScriptAdmin)
