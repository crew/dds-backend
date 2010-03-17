from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('%s.orwell.views' % settings.MODULE,
    url(r'^$', 'index', name='orwell-index'),
    url(r'^cli/manage_slide/$', 'cli_manage_slide',
        name='orwell-cli-manage-slide'),
    url(r'^cli/list_slides/$', 'cli_list_slides',
        name='orwell-cli-list-slides'),
    url(r'^slides/$', 'slide_index', name='orwell-slide-index'),
    url(r'^slides/(\d+)/$', 'slide_bundle', name='orwell-slide-bundle'),
    url(r'^clients/$', 'client_index', name='orwell-client-index'),
    url(r'^_priv/_displaycontrol/$', 'displaycontrol',
        name='orwell-displaycontrol'),
    url(r'^web-form/slide-select/$', 'web_form_slide_select',
        name='web-form-slide-select'),
    url(r'^web-form/slide-customize/(\d+)/$', 'web_form_slide_customize',
        name='web-form-slide-customize'),
    url(r'^templates/$', 'template_select', name='template-select')
    url(r'^playlists/$', 'playlist_index', name="orwell-playlist-index"),
		url(r'^playlists/(\d+)/$', 'playlist_detail', name='orwell-playlist-detail')
)

# The JSON API
urlpatterns += patterns('%s.orwell.views' % settings.MODULE,
    url(r'^json/activity/all/$', 'client_activity_all_json',
        name='orwell-json-activity-all'),
    url(r'^json/slides/(\d+)/$', 'slide_json', name='orwell-json-slide-detail'),
    url(r'^json/groups/(\d+)/$', 'group_json', name='orwell-json-group-detail'),
    url(r'^json/playlists/(\d+)/$', 'playlist_json', name='orwell-json-playlist-detail')
)
