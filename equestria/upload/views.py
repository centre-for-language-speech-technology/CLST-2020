from django.shortcuts import render
from django.views.generic import TemplateView
from .forms import UploadFileForm
from django.core.files.storage import FileSystemStorage

# Create your views here.

class UploadView(TemplateView):
	template_name = 'upload.html'

	def get(self, request):
		form = UploadFileForm()
		return render(request, self.template_name, {'form': form})

	def post(self, request):
		form = UploadFileForm(request.POST, request.FILES)
		f = request.FILES['f']
		fs = FileSystemStorage()
		fs.save(f.name,f)
		return render(request, self.template_name, {'form': form})
		