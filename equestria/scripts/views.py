from django.shortcuts import render
from .models import Process
from django.views.generic import ListView
from .models import execute_script


def start_process(request):
    if request.method == 'POST':
        execute_script()
        # Create thread
        # Execute script
        # Put stuff in DB
    else:
        pass

    return render(request, "scripts.html", {})


class ScriptListView(ListView):
    template_name = "script_list.html"
    queryset = Process.objects.all()
