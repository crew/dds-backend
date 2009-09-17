from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('%s.orwell.views' % settings.MODULE,
    (r'^$', 'index'),
    (r'^slides/(\d+)/assets/(\d+)?', 'manage_assets'),
    (r'^slides/(\d+)/$', 'slide_info'),
    (r'^slides/add/$', 'add_slide'),
    (r'^assets/add/$', 'add_asset'),
    (r'^clients/([^/]+)/$', 'clients'),
    (r'^clients/$', 'clients'),
)
