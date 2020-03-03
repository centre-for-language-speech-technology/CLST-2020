import os
from django.conf import settings
from django.shortcuts import render
from django.views.generic import TemplateView
from .forms import UploadTXTForm, UploadWAVForm
from django.core.files.storage import FileSystemStorage

# Create your views here.

class UploadWAVView(TemplateView):
	template_name = 'upload_wav2.html'

	def get(self, request):
		form = UploadWAVForm()
		return render(request, self.template_name, {'form': form})

	def post(self, request):
		form = UploadWAVForm(request.POST, request.FILES)
		wavfile = request.FILES['wavFile']
		fs = FileSystemStorage(location='media/sname/wav')
		if fs.exists('txtFile'):
			 os.remove(os.path.join(settings.MEDIA_ROOT + '/sname/wav', 'wavFile'))
		fs.save('wavFile',wavfile)
		return render(request, self.template_name, {'form': form})




class UploadTXTView(TemplateView):
	template_name = 'upload_wav2.html'

	def get(self, request):
		form = UploadTXTForm()
		return render(request, self.template_name, {'form': form})

	def post(self, request):
		form = UploadTXTForm(request.POST, request.FILES)
		txtfile = request.FILES['txtFile']
		fs = FileSystemStorage(location='media/sname/txt')
		if fs.exists('txtFile'):
			 os.remove(os.path.join(settings.MEDIA_ROOT + '/sname/txt', 'txtFile'))
		fs.save('txtFile',txtfile)
		return render(request, self.template_name, {'form': form})
		