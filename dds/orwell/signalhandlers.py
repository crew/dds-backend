# vim: set shiftwidth=4 tabstop=4 softtabstop=4 expandtab :
import datetime
import json



def write_message(message):
    # We import models here because of a circular dependency
    import models
    m = json.dumps(message)
    msgs = models.Message.objects.filter(message=m)
    if not msgs:
        models.Message(message=m).save()
    else:
        msg = msgs[0]
        msg.timestamp = datetime.datetime.now()
        msg.save()

def notify_playlist_change(playlist):
    write_message({'method': 'playlist', 'playlist':playlist.pk})

def slide_m_post_save(sender, instance, created, **kwargs):
    for playlist in instance.playlists():
        notify_playlist_change(playlist)

def slide_m_pre_delete(sender, instance, **kwargs):
    for playlist in instance.playlists():
        notify_playlist_change(playlist)

def playlist_m_post_save(sender, instance, **kwargs):
    notify_playlist_change(instance)

def client_m_post_save(sender, instance, **kwargs):
    notify_playlist_change(instance.playlist)

def pis_m_post_save(sender, instance, **kwargs):
    notify_playlist_change(instance.playlist)

pis_m_pre_delete = pis_m_post_save
pig_m_post_save = pis_m_post_save
pig_m_pre_delete = pis_m_pre_delete
