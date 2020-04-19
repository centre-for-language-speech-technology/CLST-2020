"""Module to register thing to be available in admin page."""
from django.contrib import admin
from .models import File

admin.site.register(File)

# Register your models here.
