from django.conf.urls import url
from fancybar.views import *

urlpatterns = [
	url(r'^$', Fancybar.as_view(), name='fancybar'),
	url(r'^praat_scripts$', PraatScripts.as_view(), name='praat_scripts'),
]
