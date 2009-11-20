# vim: set shiftwidth=4 tabstop=4 softtabstop=4 :
from django.conf.urls.defaults import *
from django.conf import settings

# Admin imports
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Include admin URLs
    (r'^admin/', include(admin.site.urls)),

    # FIXME Development only, we will do apache later
    (r'^media/(?P<path>.*)$', 'django.views.static.serve',
     {'document_root' : settings.MEDIA_ROOT}),

    (r'^accounts/login/$', 'django.contrib.auth.views.login'),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout'),

    (r'', include('%s.orwell.urls' % settings.MODULE)),
)
