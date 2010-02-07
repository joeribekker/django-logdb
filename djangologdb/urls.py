from django.conf import settings
from django.conf.urls.defaults import patterns
from django.contrib import admin

from djangologdb import settings as djangologdb_settings
from djangologdb import views

urlpatterns = patterns('',
    (r'datasets/$', admin.site.admin_view(views.datasets)),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': djangologdb_settings.MEDIA_ROOT}),
    )
