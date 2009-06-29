from datetime import datetime
from django.conf import settings
from dds.utils import generate_request


def j_post_save(sender, instance, created, **kwargs):
    """Send the instance to Clients that are allowed."""
    client = settings.JABBER_CLIENT

    if created:
        method_name = 'add%s' % sender.__name__
    else:
        method_name = 'update%s' % sender.__name__

    for c in instance.all_clients():
        client.send_parsed_model('%s/%s' % (c.pk, settings.J_CLIENT_RESOURCE),
                                 instance.parse(), method_name)


def j_pre_delete(sender, instance, **kwargs):
    """Notify the Clients before deleting from the database."""
    client = settings.JABBER_CLIENT

    method_name = 'remove%s' % sender.__name__

    for c in instance.all_clients():
        request = generate_request((instance.pk,), method_name)
        client.send_request('%s/%s', (c.pk, settings.J_CLIENT_RESOURCE),
                            request)


def slide_pre_save(sender, instance, **kwargs):
    """Sends the Clients a remove signal over jabber if the group for the
    slide has changed."""
    try:
        slide = sender.objects.get(pk=instance.pk)
    except:
        return

    if not instance.group == slide.group:
        for client in slide.all_clients():
            j_pre_delete(sender, slide, **kwargs)
        for client in instance.all_clients():
            j_post_save(sender, instance, True, **kwargs)


def asset_post_save(sender, instance, created, **kwargs):
    if created:
        return

    for slide in instance.all_slides():
        j_post_save(slide.__class__, slide, False, **kwargs)
