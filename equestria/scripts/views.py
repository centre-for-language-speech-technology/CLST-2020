from django.shortcuts import render
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
