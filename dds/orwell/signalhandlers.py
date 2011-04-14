"""
Signal handlers for various events on Orwell's models.
"""
import datetime
import json

def write_message(message):
    """
    Add a message to the queue of messages recieved by Harvest. message should
    be an object translatable to json (so a dictionary, list, or some basic
    value).
    """
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
    """
    Add a message to the queue read by Harvest to notify it of a change to the
    given playlist.
    """
    write_message({'method': 'playlist', 'playlist':playlist.pk})

# FIXME: slide_m_post_save and _pre_delete do the same thing. They could be the
# same function and simply given to different signalers.
def slide_m_post_save(sender, instance, created, **kwargs):
    """
    Notify Harvest that there was a change to each playlist that a given slide
    belongs to after it is saved.
    """
    for playlist in instance.playlists():
        notify_playlist_change(playlist)

def slide_m_pre_delete(sender, instance, **kwargs):
    """
    Notify Harvest that there was a change to each playlist a given slide
    belongs to before it is deleted.
    """
    for playlist in instance.playlists():
        notify_playlist_change(playlist)

def playlist_m_post_save(sender, instance, **kwargs):
    """
    Notify Harvest that there was a change to a playlist after it is saved.
    """
    notify_playlist_change(instance)

def client_m_post_save(sender, instance, **kwargs):
    """
    Notify Harvest that there was a change to a playlist after a client is
    saved.
    """
    notify_playlist_change(instance.playlist)

def pis_m_post_save(sender, instance, **kwargs):
    """
    Notify Harvest that there was a change to a playlist  after one of its
    playlist items is saved.
    """
    notify_playlist_change(instance.playlist)

pis_m_pre_delete = pis_m_post_save
