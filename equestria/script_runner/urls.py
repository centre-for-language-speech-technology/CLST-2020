from django.conf.urls import url, include
from django.urls import path
from script_runner.views import *

urlpatterns = [
    path('<str:output_file>', Outputs.as_view(), name='outputs'),
]
