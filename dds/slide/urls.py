from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('%s.slide.views' % settings.MODULE,
    (r'^(\d+)/assets/(\d+)?', 'manage_assets'),
    (r'^(\d+)/$', 'slide'),
    (r'^clients/([^/]+)/$', 'clients'),
    (r'^clients/$', 'clients'),
)

