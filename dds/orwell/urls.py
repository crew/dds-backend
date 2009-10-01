from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('%s.orwell.views' % settings.MODULE,
    url(r'^$', 'index', name='orwell-index'),
    url(r'^slides/$', 'slide_index', name='orwell-slide-index'),
    url(r'^slides/(\d+)/$', 'slide_info', name='orwell-slide-info'),
    url(r'^slides/add/$', 'add_slide', name='orwell-slide-add'),
    url(r'^assets/add/$', 'add_asset', name='orwell-asset-add'),
    url(r'^clients/$', 'client_index', name='orwell-clients-index'),
)
