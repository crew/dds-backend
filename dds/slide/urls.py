from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('%s.dds.views' % settings.MODULE,
    (r'^(\d+)/assets/(\d+)?', 'manage_assets'),
)

