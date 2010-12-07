from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('%s.orwell.views' % settings.MODULE,
    url(r'^$', 'index', name='orwell-index'),
    url(r'^slides/$', 'slide_index', name='orwell-slide-index'),
    url(r'^slides/create/$', 'slide_create', name='orwell-create-slide'),
    url(r'^slides/create-pdf/$', 'pdf_slide_create', name='orwell-create-pdf-slide'),
    url(r'^slides/edit/$', 'slide_edit', name='orwell-slide-edit'),
    url(r'^slides/(\d+)/$', 'slide_bundle', name='orwell-slide-bundle'),
    url(r'^clients/$', 'client_index', name='orwell-client-index'),
    url(r'^_priv/_displaycontrol/$', 'displaycontrol',
        name='orwell-displaycontrol'),
    url(r'^web-form/slide-select/$', 'web_form_slide_select',
        name='web-form-slide-select'),
    url(r'^web-form/slide-customize/(\d+)/$', 'web_form_slide_customize',
        name='web-form-slide-customize'),
    url(r'^templates/$', 'template_select', name='template-select'),
    url(r'^playlists/(\d+)/$', 'playlist_detail',
        name='orwell-playlist-detail'),
)

urlpatterns += patterns('django.views.generic.simple',
    url(r'^playlists/$', 'direct_to_template',
        {'template': 'orwell/playlist-index.html'}, name='orwell-playlist-index'),
)

# CLI API
urlpatterns += patterns('%s.orwell.cli_views' % settings.MODULE,
    url(r'^cli/manage_slide/$', 'cli_manage_slide',
        name='orwell-cli-manage-slide'),
    url(r'^cli/list_slides/$', 'cli_list_slides',
        name='orwell-cli-list-slides'),
)

# The JSON API
urlpatterns += patterns('%s.orwell.views' % settings.MODULE,
    url(r'^json/activity/all/$', 'client_activity_all_json',
        name='orwell-json-activity-all'),
    url(r'^json/slides/(\d+)/$', 'slide_json', name='orwell-json-slide-detail'),
    url(r'^json/playlists/(\d+)/$', 'playlist_json',
        name='orwell-json-playlist-detail'),
    url(r'^json/playlists/$', 'playlist_list_json',
        name="orwell-json-playlist-list"),
    url(r'^json/clients/$', 'client_json',
        name="orwell-client-json"),
)
