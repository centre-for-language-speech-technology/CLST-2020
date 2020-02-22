from django.shortcuts import render
from django.http import HttpResponseNotFound
from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.db.models import Q
from fancybar.models import *


# Create your views here.

class GenericTemplate(TemplateView):
        template_name = 'template.html'

        def get(self, request):
                return render(request, self.template_name)


        def post(self, request):
                return render(request, self.template_name)

        
       
class Fancybar(GenericTemplate):
        template_name = 'template.html'


class PraatScripts(TemplateView):
        template_name = 'praat_scripts.html'

        arg = {
                'scripts': PraatScripts.objects.all(),
        }
        
        def get(self, request):
                return render(request, self.template_name, self.arg)

        
        def post(self, request):
                return render(request, self.template_name)
