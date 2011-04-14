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
    Add a Message to the queue read by Harvest to notify it of a change to the
    given Playlist.
    """
    write_message({'method': 'playlist', 'playlist':playlist.pk})

def slide_change_notification(sender, instance, *args, **kwargs):
    """
    Notify Harvest that there was a change to each Playlist that a given slide
    belongs to.
    """
    for playlist in instance.playlists():
        notify_playlist_change(playlist)

def playlist_notification(sender, instance, **kwargs):
    """
    Notify Harvest that there was a change to a Playlist.
    """
    notify_playlist_change(instance)

def playlist_relation_notification(sender, instance, **kwargs):
    """
    Notify Harvest that there was a change to a model that has a Playlist as a
    field.
    """
    notify_playlist_change(instance.playlist)
