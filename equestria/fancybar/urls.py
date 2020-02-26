from django.conf.urls import url, include
from fancybar.views import *

urlpatterns = [
	url(r'^$', Fancybar.as_view(), name='fancybar'),
	url(r'^praat_scripts$', PraatScripts.as_view(), name='praat_scripts'),
	url(r'upload_wav', UploadWav.as_view(), name='upload_wav'),
	url(r'upload_txt', UploadTxt.as_view(), name='upload_txt'),
	url(r'forced_alignment', ForcedAlignment.as_view(), name='forcedd_alignment'),
	url(r'update_dictionary', UpdateDictionary.as_view(), name='update_dictionary'),
	url(r'auto_segmentation', AutoSegmentation.as_view(), name='auto_segmentation'),
	url(r'download_results', DownloadResults.as_view(), name='download_results'),
]
