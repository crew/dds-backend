from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('%s.slide.views' % settings.MODULE,
    (r'^(\d+)/assets/(\d+)?', 'manage_assets'),
    (r'^(\d+)/$', 'slide'),
    (r'^add/$', 'slide_add'),
    (r'^add-asset/$', 'asset_add'),
    (r'^clients/([^/]+)/$', 'clients'),
    (r'^clients/$', 'clients'),
)
