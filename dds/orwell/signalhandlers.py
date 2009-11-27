import json


def slide_m_pre_save(sender, instance, **kwargs):
    from models import Message
    try:
        sender.objects.get(pk=instance.pk)
    except:
        return
    message = {'method': 'add', 'slide': instance.pk,
               'assets': instance.assets.count()}
    Message(message=json.dumps(message)).save()


def slide_m_post_save(sender, instance, created, **kwargs):
    from models import Message
    if created:
        message = {'method': 'add', 'slide': instance.pk,
                   'assets': instance.assets.count()}
        Message(message=json.dumps(message)).save()


def slide_m_pre_delete(sender, instance, **kwargs):
    from models import Message
    message = {'method': 'delete', 'slide': instance.pk}
    Message(message=json.dumps(message)).save()


def client_to_group_pre_save(sender, instance, **kwargs):
    from models import Message
    try:
        ctg = sender.objects.get(pk=instance.pk)
    except:
        # It is being created, do nothing.
        return

    # The group differs, so remove the old group.
    if ctg.group != instance.group:
        for s in ctg.group.slides.all():
            message = {'method': 'delete', 'slide': s.pk,
                       'to': ctg.client.jid()}
            Message(message=json.dumps(message)).save()


def client_to_group_post_save(sender, instance, created, **kwargs):
    from models import Message
    group = instance.group
    for s in group.slides.all():
        message = {'method': 'add', 'slide': s.pk,
                   'to': instance.client.jid()}
        Message(message=json.dumps(message)).save()


# TODO client_to_group_pre_delete
