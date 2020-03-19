import os
from django.conf import settings
from django.shortcuts import render
from django.views.generic import TemplateView
from .forms import UploadTXTForm, UploadWAVForm
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


def safeFile(request,form,filetype):
    """Function to safe uploaded file"""
    print("valid form")
    uploadedfile = request.FILES[filetype]
    loc = "media/sname/" + filetype
    fs = FileSystemStorage(location=loc)
    if fs.exists(uploadedfile.name):
        os.remove(
            os.path.join(
                settings.MEDIA_ROOT + "/sname/" + filetype, uploadedfile.name
            )
        )
    fs.save(uploadedfile.name, uploadedfile)

class UploadWAVView(TemplateView):
    """ Class to handle the upload/wav page. Also acts as callback URL for the uploads in forced alignment page"""
    template_name = "upload_wav2.html"


    def get(self, request):
        """function to handle get requests to upload/wav"""
        if not request.user.is_authenticated:
            return redirect("%s?next=%s" % (settings.LOGIN_URL, request.path))
        else:
            form = UploadWAVForm()
            return render(request, self.template_name, {"WAVform": form})

    def post(self, request):
        """function to handle post requests to upload/wav. Also acts as callback function from forced alignment page"""
        if not request.user.is_authenticated:
            return redirect("%s?next=%s" % (settings.LOGIN_URL, request.path))
        else:
            form = UploadWAVForm(request.POST, request.FILES)
            if form.is_valid():
                safeFile(request,form,"wavFile")
            else:
                print("invalid form")
                print(form.errors)
                # return error to AJAX function to print
            return HttpResponseRedirect("/forced/")


class UploadTXTView(TemplateView):
    """ Class to handle the upload/txt page. Also acts as callback URL for the uploads in forced alignment page"""
    template_name = "upload_txt2.html"

#    def safeFile(self,request,form):
#        """Function to safe uploaded txt file"""
#        print("valid form")
#        txtfile = request.FILES["txtFile"]
#        fs = FileSystemStorage(location="media/sname/txt")
#        if fs.exists(txtfile.name):
#            os.remove(
#                os.path.join(
#                    settings.MEDIA_ROOT + "/sname/txt", txtfile.name
#                )
#            )
#        fs.save(txtfile.name, txtfile)

    def get(self, request):
        """function to handle get requests to upload/txt"""
        if not request.user.is_authenticated:
            return redirect("%s?next=%s" % (settings.LOGIN_URL, request.path))
        else:
            form = UploadTXTForm()
            return render(request, self.template_name, {"TXTform": form})

    def post(self, request):
        """function to handle post requests to upload/txt. Also acts as callback function from forced alignment page"""
        if not request.user.is_authenticated:
            #redirect user to login page if not logged in
            return redirect("%s?next=%s" % (settings.LOGIN_URL, request.path))
        else:
            form = UploadTXTForm(request.POST, request.FILES)
            if form.is_valid():
                #safe file if form is valid
                safeFile(request,form,"txtFile")
            else:
                print("invalid form")
                print(form.errors)
                # return error to AJAX function to print
            return HttpResponseRedirect("/forced/")
