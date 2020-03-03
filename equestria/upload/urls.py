from django.contrib import admin
from django.urls import path, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from django.conf import settings
from .views import UploadTXTView, UploadWAVView

urlpatterns = [
    path('wav', UploadWAVView.as_view(), name="uploadwav_form"),
    path('txt', UploadTXTView.as_view(), name="uploadtxt_form"),
]


urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)