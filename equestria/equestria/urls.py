from django.conf.urls import include
from django.views.static import serve
from django.contrib import admin
from django.urls import include, path
from scripts.views import start_process
from . import settings
from django.contrib.staticfiles.urls import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('index/', start_process),
    path('admin/', admin.site.urls),
    path('', include(('fancybar.urls', 'fancybar'), namespace='fancybar')),
    path('upload/', include(('upload.urls', 'upload'), namespace='upload'))
]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
