# vim: set tabstop=4 softtabstop=4 shiftwidth=4 expandtab :
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'dds.settings'
from dds.utils import generate_request
from dds.orwell.models import Location, Client, Slide
from django.contrib.auth.models import Group

__author__ = 'Alex Lee <lee@ccs.neu.edu>'


def get_default_location():
    location, _ = Location.objects.get_or_create(name='Unknown')
    return location


def get_default_group():
    group, _ = Group.objects.get_or_create(name='Unregistered clients')
    return group


def get_client(jid):
    """Gets the Client from Django, if one exists."""
    client, created = Client.objects.get_or_create(pk=jid,
                          defaults={'location': get_default_location(), })
    if created:
        client.groups.add(get_default_group())
        client.save()
    return client, created


def get_slide(pk):
    try:
        slide = Slide.objects.get(pk=pk)
    except:
        return None
    return slide


def get_activity(jid):
    return ClientActivity.get_or_create(pk=jid)


def generate_request(*args, **kwargs):
    return dds.utils.generate_request(*args, **kwargs)
