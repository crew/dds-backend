# vim: set shiftwidth=4 tabstop=4 softtabstop=4 :
from django.db import models
from django.contrib.auth.models import User, Group
from django.conf import settings
from django.core.urlresolvers import reverse
from utils import register_signals, temp_upload_to
import hashlib
import signalhandlers
import shutil
import os
import json
from datetime import datetime


class Slide(models.Model):
    UPLOAD_PATH = 'slidethumbnails'
    MODE_CHOICES = (
        (0, 'layout'),
        (1, 'module'),
        (2, 'executable'),
    )
    TRANSITION_CHOICES = (
        (0, 'fade'),
        (1, 'slide-right-left'),
        (2, 'slide-left-right'),
        (3, 'slide-up-down'),
        (4, 'slide-down-up'),
    )

    title = models.CharField(max_length=512)
    user = models.ForeignKey(User, related_name='slides')
    group = models.ForeignKey(Group, related_name='slides')
    priority = models.IntegerField()
    duration = models.IntegerField()
    expires_at = models.DateTimeField(null=True, default=None)
    mode = models.IntegerField(choices=MODE_CHOICES, default=0)
    transition = models.IntegerField(choices=TRANSITION_CHOICES, default=0)
    last_update = models.DateTimeField(auto_now=True)
    assets = models.ManyToManyField('Asset', related_name='slides', blank=True)
    thumbnail = models.FileField(max_length=300, upload_to=temp_upload_to,
                                 null=True, blank=True)

    def all_assets(self):
        """Return the list of Assets used by this Slide."""
        return self.assets.all()

    def all_clients(self):
        """Return the list of Clients allowed to display this Slide."""
        return self.group.clients.all()

    def parse(self):
        """Return a tuple of slide metadata and the assets where a slide is a
        hash of its id and priority and an asset is a hash of its id and url.
        """
        slide = { 'id'              : self.id,
                  'priority'        : self.priority,
                  'duration'        : self.duration,
                  'mode'            : self.get_mode_display(),
                  'transition'      : self.get_transition_display(), }
                  #'expiration_date' : self.expiration_date, }

        assets = [{'id' : a.id, 'url' : a.url()} for a in self.assets.all()]

        return (slide, assets)

    def get_class_tags(self):
        """Get a list of textual tags for this slide."""
        return 'slide-group-%d' % self.group.id

    def thumbnail_name(self):
        return os.path.basename(self.thumbnail.name)

    def thumbnailurl(self):
        if self.thumbnail:
            return '%s/%s/%d/%s' % (settings.MEDIA_URL, self.UPLOAD_PATH,
                                    self.pk,
                                    self.thumbnail_name())
        else:
            return '%s/images/unknown.png' % settings.MEDIA_URL

    def allowed(self, user):
        return self.group in user.groups or user.is_staff

    def __unicode__(self):
        return '%s %s %s' % (self.title, self.user, self.group)

    def upload_dir(self):
        return '%s/%s/%d' % (settings.MEDIA_ROOT, self.__class__.UPLOAD_PATH,
                             self.pk)

    def _acquire_pk(self):
        """Pre-allocate the primary key by creating an empty object and saving
        it, but only if needed.
        >>> a = Asset()
        >>> not a.pk
        True
        >>> not a._acquire_pk()
        False
        """
        if not self.pk:
            temp = self.__class__()
            super(temp.__class__, temp).save()
            self.pk = temp.pk
        return self.pk

    def save(self, force_insert=False, force_update=False):
        """Adds a scaffold option. When scaffold is True, the file field
        is not renamed."""
        self._acquire_pk()

        # Load the file onto the file system
        super(self.__class__, self).save(force_insert=force_insert,
                                         force_update=force_update)

        if not self.thumbnail.name:
            return

        if not self.thumbnail.closed:
            self.thumbnail.close()

        # Create the new directory.
        file_new_dir = self.upload_dir()
        if not os.path.isdir(file_new_dir):
            os.makedirs(file_new_dir, 0755)

        # Find the new path
        file_new_path = os.path.join(file_new_dir,
                                     os.path.basename(self.thumbnail.path))

        # XXX Should we remove the old file or not?
        # Move the file, then delete the temporary directory.
        shutil.move(self.thumbnail.path, file_new_path)
        temp_dir = os.path.dirname(self.thumbnail.path)
        if len(os.listdir(temp_dir)) == 0:
            os.rmdir(temp_dir)
        self.thumbnail = file_new_path

        super(self.__class__, self).save(force_insert=force_insert,
                                         force_update=force_update)

# Signals for Slide
register_signals(Slide, pre_save=signalhandlers.slide_pre_save,
                        post_save=signalhandlers.j_post_save,
                        pre_delete=signalhandlers.j_pre_delete)


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

    def id_user_part(self):
        return self.client_id.split('@')[0]

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
        ssbase = '%s/%s' % (settings.MEDIA_URL, Slide.SCREENSHOT_DIR)
        if not self.active():
            # XXX Hack. This needs to be fixed to be path agnostic
            #     and configurable.
            path = '%s/images/offline.png' % settings.MEDIA_URL
            caption = 'Client Offline'
        else:
            path = self.currentslide().thumbnailurl()
            caption = self.currentslide().title
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
                 post_save=signalhandlers.client_to_group_post_save)


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
        p['client']['url'] = reverse('orwell-client-info', args=[c.pk])
        slide_info = c.slideinfo()
        p['client']['screenshot'] = slide_info[0]
        p['client']['caption'] = slide_info[1]
        p['slide'] = None
        if self.current_slide:
            s = self.current_slide
            p['slide'] = s.__dict__
            p['slide']['url'] = reverse('orwell-slide-info', args=[s.pk])
        return p

    def json(self):
        return json.dumps(self.parse(), default=str)

    class Meta:
        verbose_name = 'activity'
        verbose_name_plural = 'activities'


class Asset(models.Model):
    UPLOAD_PATH = 'assets'

    name = models.CharField(max_length=200, blank=True)
    description = models.CharField(max_length=500, blank=True)
    last_update = models.DateTimeField(auto_now=True)
    file = models.FileField(max_length=300, upload_to=temp_upload_to,
                            null=True)

    def all_slides(self):
        """Returns all Slides that use this Asset."""
        return self.slides.all()

    def all_clients(self):
        """Returns all Clients that use this Asset."""
        client_list = set()
        for s in self.slides.all():
            client_list.update(s.all_clients())
        return client_list

    def file_name(self):
        return os.path.basename(self.file.name)

    def url(self):
        return '%s/%s/%d/%s' % (settings.MEDIA_URL, self.UPLOAD_PATH, self.pk,
                                self.file_name())

    def __unicode__(self):
        return '%s' % (self.file)

    def parse(self):
        """Returns a tuple of a hash of its id and url.
        Note: This raises an exception for an object that is just an Asset.
        """
        return ({'id' : self.id, 'url' : self.url() },)

    def upload_dir(self):
        return '%s/%s/%d' % (settings.MEDIA_ROOT, self.__class__.UPLOAD_PATH,
                             self.pk)

    def is_temporary(self):
        if not self.file:
            return True
        p = self.file.path
        return p.startswith('%s/%s/' % (settings.MEDIA_ROOT, 'tmp'))

    def _acquire_pk(self):
        """Pre-allocate the primary key by creating an empty object and saving
        it, but only if needed.
        >>> a = Asset()
        >>> not a.pk
        True
        >>> not a._acquire_pk()
        False
        """
        if not self.pk:
            temp = self.__class__()
            super(temp.__class__, temp).save()
            self.pk = temp.pk
        return self.pk

    def save(self, force_insert=False, force_update=False):
        """Adds a scaffold option. When scaffold is True, the file field
        is not renamed."""
        self._acquire_pk()

        # Load the file onto the file system
        super(self.__class__, self).save(force_insert=force_insert,
                                         force_update=force_update)

        if not self.file.name:
            return

        if not self.file.closed:
            self.file.close()

        # Create the new directory.
        file_new_dir = self.upload_dir()
        if not os.path.isdir(file_new_dir):
            os.makedirs(file_new_dir, 0755)

        # Find the new path
        file_new_path = os.path.join(file_new_dir,
                                     os.path.basename(self.file.path))

        # XXX Should we remove the old file or not?
        # Move the file, then delete the temporary directory.
        shutil.move(self.file.path, file_new_path)
        temp_dir = os.path.dirname(self.file.path)
        if len(os.listdir(temp_dir)) == 0:
            os.rmdir(temp_dir)
        self.file = file_new_path

        super(self.__class__, self).save(force_insert=force_insert,
                                         force_update=force_update)


# Signals for Asset
register_signals(Asset, post_save=signalhandlers.asset_post_save,
                        pre_delete=signalhandlers.j_pre_delete)
