from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('%s.orwell.views' % settings.MODULE,
    url(r'^$', 'index', name='orwell-index'),
    url(r'^slides/(\d+)/assets/(\d+)?', 'manage_assets'),
    url(r'^slides/(\d+)/$', 'slide_info', name='orwell-slide-info'),
    url(r'^slides/add/$', 'add_slide', name='orwell-slide-add'),
    url(r'^assets/add/$', 'add_asset', name='orwell-asset-add'),
    url(r'^clients/([^/]+)/$', 'clients'),
    url(r'^clients/$', 'clients', name='orwell-clients-index'),
)
