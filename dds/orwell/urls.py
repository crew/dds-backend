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
    url(r'^playlists/$', 'playlist_index', name='orwell-playlist-index'),
    url(r'^playlists/create/$', 'playlist_create', name='orwell-create-playlist'),
    url(r'^playlists/create/item$', 'playlistitem_create', name='orwell-create-playlistitem'),
    url(r'^playlists/(\d+)/$', 'playlist_edit', name='orwell-playlist-edit'),
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
