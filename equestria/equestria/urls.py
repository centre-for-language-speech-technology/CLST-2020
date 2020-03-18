from django.contrib import admin
from django.urls import include, path
from . import settings
from django.contrib.staticfiles.urls import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(('fancybar.urls', 'fancybar'), namespace='fancybar')),
    path('upload/', include(('upload.urls', 'upload'), namespace='upload')),
    path('forced/', include(('forcedAlign.urls', 'forced'), namespace='forcedAlign')),
    path('outputs/', include(('script_runner.urls',
                              'script_runner'), namespace='script_runner')),
    path('accounts/',include(('accounts.urls',
                              'accounts'), namespace='accounts'))
    ]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
