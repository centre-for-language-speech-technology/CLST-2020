from django.shortcuts import render
<<<<<<< HEAD
from .models import Process
from django.views.generic import ListView
=======
from .models import execute_script
>>>>>>> parent of 193d483... Process write to JSON


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
