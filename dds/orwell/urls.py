from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('%s.orwell.views' % settings.MODULE,
    url(r'^$', 'index', name='orwell-index'),
    url(r'^slides/$', 'slide_index', name='orwell-slide-index'),
    url(r'^slides/(\d+)/$', 'slide_bundle', name='orwell-slide-bundle'),
    url(r'^clients/$', 'client_index', name='orwell-client-index'),
)

# The JSON API
urlpatterns += patterns('%s.orwell.views' % settings.MODULE,
    url(r'^json/activity/all/$', 'client_activity_all_json',
        name='orwell-json-activity-all'),
)
