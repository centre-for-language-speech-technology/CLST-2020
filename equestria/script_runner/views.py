from django.views.generic import TemplateView
from django.shortcuts import render

# Create your views here.


class Outputs(TemplateView):

    def get(self, request, output_file):
        return render(request, output_file)

    def post(self, request, output_file):
        return render(request, output_file)
