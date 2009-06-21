from datetime import datetime
from django.conf import settings
from dds.utils import generate_request

def j_post_save(sender, instance, created, **kwargs):
    """ sends the instance to Clients that are allowed """
    client = settings.JABBER_CLIENT

    if created:
        format = 'add%s'
    else:
        format = 'update%s'
 
    for c in instance.all_clients():
        client.send_parsed_model('%s/%s' % (c.pk, settings.J_CLIENT_RESOURCE),
                                 instance.parse(), format % sender.__name__)

def j_pre_delete(sender, instance, **kwargs):
    """ before deleting from the database, notify the Clients """
    client = settings.JABBER_CLIENT

    for c in instance.all_clients():
        request = generate_request((instance.pk,), 'remove' + sender.__name__)
        client.send_request('%s/%s', (c.pk, settings.J_CLIENT_RESOURCE),
                            request)


def slide_pre_save(sender, instance, **kwargs):
    """ Sends the Clients a remove signal over jabber if the group for
    the slide has changed. """
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

