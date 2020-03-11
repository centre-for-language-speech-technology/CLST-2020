from .models import Process
from django.views.generic import ListView

class ScriptListView(ListView):
    template_name = "script_list.html"
    queryset = Process.objects.all()
