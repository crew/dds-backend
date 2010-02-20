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

def notify_playlist_change(playlist)
    write_message({'method': 'playlist', 'playlist':playlist.pk})

def slide_m_pre_save(sender, instance, **kwargs):
    try:
        sender.objects.get(pk=instance.pk)
    except:
        return
    message = {'method': 'add', 'slide': instance.pk}
    write_message(message)


def slide_m_post_save(sender, instance, created, **kwargs):
    if created:
        message = {'method': 'add', 'slide': instance.pk }
        write_message(message)


def slide_m_pre_delete(sender, instance, **kwargs):
    message = {'method': 'delete', 'slide': instance.pk}
    write_message(message)


def playlist_m_pre_save(sender, instance, **kwargs):
    try:
        sender.objects.get(pk=instance.pk)
    except:
        return
    message = {'method': 'playlist', 'playlist':instance.pk}
    write_message(message)


def playlist_m_post_save(sender, instance, created, **kwargs):
    if created:
        message = {'method': 'playlist', 'playlist':instance.pk}
        write_message(message)


def playlist_m_pre_delete(sender, instance, **kwargs):
    pass


def ctg_write_message(instance, method):
    for s in instance.group.slides.all():
        message = {'method': method, 'slide': s.pk,
                   'to': instance.client.jid()}
        write_message(message)

