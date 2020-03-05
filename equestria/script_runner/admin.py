from django.contrib import admin
from script_runner import models

# Register your models here.


class ArgumentInline(admin.StackedInline):
    model = models.Argument


class ScriptA(admin.ModelAdmin):
    inlines = [
        ArgumentInline,
    ]


admin.site.register(models.Script, ScriptA)
