from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('%s.orwell.views' % settings.MODULE,
    url(r'^$', 'index', name='orwell-index'),
    url(r'^slides/$', 'slide_index', name='orwell-slide-index'),
    url(r'^slides/(\d+)/$', 'slide_info', name='orwell-slide-info'),
    url(r'^slides/add/$', 'add_slide', name='orwell-slide-add'),
    url(r'^assets/$', 'asset_index', name='orwell-asset-index'),
    url(r'^assets/(\d+)/$', 'asset_info', name='orwell-asset-info'),
    url(r'^assets/add/$', 'add_asset', name='orwell-asset-add'),
    url(r'^clients/$', 'client_index', name='orwell-client-index'),
    url(r'^clients/add/$', 'add_client', name='orwell-client-add'),
    url(r'^clients/(.+)/$', 'client_info', name='orwell-client-info'),
    url(r'^(\d+)/assets/(\d+)?', 'manage_assets'),
)

# The JSON API
urlpatterns += patterns('%s.orwell.views' % settings.MODULE,
    url(r'^json/activity/all/$', 'client_activity_all_json'),
)
