import os
from django.conf import settings
from django.shortcuts import render
from django.views.generic import TemplateView
from upload.forms import UploadTXTForm, UploadWAVForm
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

# Create your views here.


class FAView(TemplateView):
    """Class to handle get requests to the forced alignment page."""

    """Forced allignment view."""

    template_name = "ForcedAlign.html"

    def get(self, request):

        """Handle requests to the /forced page.
        
        Get requests are handled wihtin this class while the upload
        post requests are handled in the upload app
        with callback URLs upload/wav and upload/txt.
        """
        if not request.user.is_authenticated:
            return redirect("%s?next=%s" % (settings.LOGIN_URL, request.path))
        else:
            wavForm = UploadWAVForm()
            txtForm = UploadTXTForm()
            return render(
                request,
                self.template_name,
                {"WAVform": wavForm, "TXTform": txtForm},
            )
