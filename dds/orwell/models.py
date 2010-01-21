# vim: set shiftwidth=4 tabstop=4 softtabstop=4 expandtab :
from django.db import models
from django.contrib.auth.models import User, Group
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.urlresolvers import reverse
from utils import register_signals, temp_upload_to, scaffolded_save
import hashlib
import signalhandlers
import shutil
import os
import json
from datetime import datetime, timedelta

class RecentManager(models.Manager):

    def get_query_set(self):
        qs = super(self.__class__, self).get_query_set()
        five_minutes_ago = datetime.now() - timedelta(seconds=60 * 5)
        return qs.filter(timestamp__lt=five_minutes_ago)


class Message(models.Model):
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now=True)

    objects = models.Manager()
    recent = RecentManager()

    def tuple(self):
        return self.message, self.timestamp

    def __unicode__(self):
        return str(self.tuple())

class Slide(models.Model):
    title = models.CharField(max_length=512)
    user = models.ForeignKey(User, related_name='slides')
    group = models.ForeignKey(Group, related_name='slides')
    priority = models.IntegerField()
    duration = models.IntegerField()
    expires_at = models.DateTimeField(null=True, default=None)
    last_update = models.DateTimeField(auto_now=True)
    thumbnail = models.ImageField(max_length=300, upload_to="thumbs/%Y%H%M%S",
                                  null=True)
    bundle = models.FileField(max_length=300, upload_to="slides/%Y%H%M%S",
                              null=True)

    def all_clients(self):
        """Return the list of Clients allowed to display this Slide."""
        return self.group.clients.all()

    def parse(self):
        """Returns slide metadata as a dictionary of its id, bundle url,
        priority, duration, and expiration date.
        """
        slide = { 'id'              : self.id,
                  'url'             : self.bundle.url,
                  'priority'        : self.priority,
                  'duration'        : self.duration }

        return slide

    def get_class_tags(self):
        """Get a list of textual tags for this slide."""
        return 'slide-group-%d' % self.group.id

    def allowed(self, user):
        return self.group in user.groups or user.is_staff

    @models.permalink
    def get_absolute_url(self):
        return ('orwell-slide-bundle', [str(self.id)])

    def __unicode__(self):
        return '%s %s %s' % (self.title, self.user, self.group)

    def thumbnailurl(self):
        return self.thumbnail.url
    
    def populate_from_bundle(self, bundle, tarfileobj):
        manifest = json.load(tarfileobj.extractfile('manifest.js'))
        if 'priority' in manifest:
            self.priority = int(manifest['priority'])
        if 'duration' in manifest:
            self.duration = int(manifest['duration'])
        if 'title' in manifest:
            self.title = str(manifest['title'])
        if 'thumbnail_img' in manifest:
            p = manifest['thumbnail_img']
            self.thumbnail.save(p,
                                ContentFile(tarfileobj.extractfile(p).read()))
        self.bundle = bundle
        self.save()

# Signals for Slide
register_signals(Slide, pre_save=signalhandlers.slide_m_pre_save,
                        post_save=signalhandlers.slide_m_post_save,
                        pre_delete=signalhandlers.slide_m_pre_delete)


class Location(models.Model):
    name = models.CharField(max_length=500)

    def __unicode__(self):
        return '%s' % self.name


class Client(models.Model):
    """Represents a DDS Jabber client."""
    name = models.CharField(max_length=100, default='Unnamed')
    client_id = models.EmailField(max_length=128, primary_key=True)
    location = models.ForeignKey(Location, null=True, related_name='clients')
    groups = models.ManyToManyField(Group, through='ClientToGroup',
                                    related_name='clients')

    def jid(self):
        """The jabber id of the client."""
        return '%s/%s' % (self.pk, settings.J_CLIENT_RESOURCE)

    # XXX hack, the add function should wait till Client's save
    #     to do the actual save.
    def __getattribute__(self, name):
        if name == 'groups':
            gs = object.__getattribute__(self, name)
            gs.add = self.add_groups
            return gs
        return models.Model.__getattribute__(self, name)

    def last_contact(self):
        try:
            return self.activity.last_update
        except:
            pass

    def id_hash(self):
        hash = hashlib.md5()
        hash.update(self.client_id)
        return hash.hexdigest()

    def displayname(self):
        if self.name == 'Unnamed':
            return self.client_id.split('@')[0]
        else:
            return self.name

    def all_slides(self):
        """Return all the Slides allowed."""
        slide_list = set()
        for g in self.groups.all():
            slide_list.update(g.slides.all())
        return slide_list

    def active(self):
        try:
            return self.activity.active
        except:
            return False

    def currentslide(self):
        if not self.active():
            return None
        else:
            return self.activity.current_slide

    def get_class_tags(self):
        """Get a list of textual tags for this slide."""
        tags = ['client-location-%s' % self.location.id]
        for group in self.groups.all():
            tags.append('client-group-%s' % group.id)
        if self.active():
            tags.append('client-online')
        else:
            tags.append('client-offline')
        return ' '.join(tags)

    def slideinfo(self):
        curslide = self.currentslide()
        if curslide is None:
            path = os.path.join(settings.MEDIA_URL, 'images', 'offline.png')
            caption = 'Client Offline'
        else:
            path = curslide.thumbnailurl()
            caption = curslide.title
        return path, caption

    def thumbnailurl(self):
        return self.slideinfo()[0]

    def slidecaption(self):
        return self.slideinfo()[1]

    def add_group(self, group):
        c_to_g = ClientToGroup(client=self, group=group)
        try:
            c_to_g.save()
        except:
            pass

    def add_groups(self, *groups):
        for g in groups:
            self.add_group(g)

    def __unicode__(self):
        return '%s@%s' % (self.pk, self.location)


class ClientToGroup(models.Model):
    client = models.ForeignKey(Client, related_name='client_and_groups')
    group = models.ForeignKey(Group, related_name='client_and_groups')

    class Meta:
        unique_together = ['client', 'group']


register_signals(ClientToGroup,
                 pre_save=signalhandlers.client_to_group_pre_save,
                 post_save=signalhandlers.client_to_group_post_save,
                 pre_delete=signalhandlers.client_to_group_pre_delete)


class ClientActivity(models.Model):
    client = models.OneToOneField(Client, primary_key=True,
                                  related_name='activity')
    current_slide = models.ForeignKey(Slide, null=True, blank=True,
                                      related_name='activities')
    active = models.BooleanField(default=False)
    last_update = models.DateTimeField(auto_now=True)

    def parse(self):
        p = self.__dict__
        c = self.client
        p['client'] = c.__dict__
        p['client']['hash'] = c.id_hash()
        slide_info = c.slideinfo()
        p['client']['screenshot'] = slide_info[0]
        p['client']['caption'] = slide_info[1]
        p['slide'] = None
        if self.current_slide:
            s = self.current_slide
            p['slide'] = s.__dict__
        return p

    def json(self):
        return json.dumps(self.parse(), default=str)

    class Meta:
        verbose_name = 'activity'
        verbose_name_plural = 'activities'
