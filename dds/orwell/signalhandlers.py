# vim: set shiftwidth=4 tabstop=4 softtabstop=4 expandtab :
import datetime
import json

import models


def write_message(message):
    # XXX There is some weird import issue
    m = json.dumps(message)
    msgs = models.Message.objects.filter(message=m)
    if not msgs:
        models.Message(message=m).save()
    else:
        msg = msgs[0]
        msg.timestamp = datetime.datetime.now()
        msg.save()


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


def ctg_write_message(instance, method):
    for s in instance.group.slides.all():
        message = {'method': method, 'slide': s.pk,
                   'to': instance.client.jid()}
        write_message(message)


def client_to_group_pre_save(sender, instance, **kwargs):
    try:
        old = sender.objects.get(pk=instance.pk)
    except:
        # It is being created, do nothing.
        return

    # The group differs, so remove the old group.
    if old.group != instance.group:
        ctg_write_message(old, 'delete')


def client_to_group_post_save(sender, instance, created, **kwargs):
    ctg_write_message(instance, 'add')


def client_to_group_pre_delete(sender, instance, **kwargs):
    ctg_write_message(instance, 'delete')
