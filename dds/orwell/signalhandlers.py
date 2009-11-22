from datetime import datetime
from django.conf import settings
from dds.utils import generate_request


def j_post_save(sender, instance, created, **kwargs):
    """Send the instance to Clients that are allowed."""
    jabber = settings.JABBER_CLIENT

    if created:
        method_name = 'add%s' % sender.__name__
    else:
        method_name = 'update%s' % sender.__name__

    for c in instance.all_clients():
        jabber.send_parsed_model(c.jid(), instance.parse(), method_name)


def j_pre_delete(sender, instance, **kwargs):
    """Notify the Clients before deleting from the database."""
    jabber = settings.JABBER_CLIENT

    method_name = 'remove%s' % sender.__name__

    for c in instance.all_clients():
        request = generate_request((instance.pk,), method_name)
        jabber.send_request(c.jid(), request)


def slide_pre_save(sender, instance, **kwargs):
    """Sends the Clients a remove signal over jabber if the group for the
    slide has changed."""
    try:
        slide = sender.objects.get(pk=instance.pk)
    except:
        return

    if not instance.group == slide.group:
        j_pre_delete(sender, slide, **kwargs)
        j_post_save(sender, instance, True, **kwargs)


def asset_post_save(sender, instance, created, **kwargs):
    if created or instance.is_temporary():
        return

    for slide in instance.all_slides():
        j_post_save(slide.__class__, slide, False, **kwargs)


def client_to_group_pre_save(sender, instance, **kwargs):
    jabber = settings.JABBER_CLIENT
    try:
        ctg = sender.objects.get(pk=instance.pk)
    except:
        # It is being created, do nothing.
        return

    # The group differs, so remove the old group.
    if ctg.group != instance.group:
        for s in ctg.group.slides.all():
            request = generate_request((s.pk,), 'removeSlide')
            jabber.send_request(instance.client.jid(), request)


def client_to_group_post_save(sender, instance, created, **kwargs):
    jabber = settings.JABBER_CLIENT
    group = instance.group
    for s in group.slides.all():
        request = generate_request((s.pk,), 'addSlide')
        jabber.send_request(instance.client.jid(), request)
