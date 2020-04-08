from django.contrib import admin
from accounts.models import *

"""Module to register user model at admin page."""

# Register your models here.
admin.site.register(UserProfile)
