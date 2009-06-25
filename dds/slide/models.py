from django.db import models
from django.contrib.auth.models import User, Group
from django.conf import settings
from utils import register_signals, temp_upload_to
import signalhandlers
import shutil
import os
from os import path
from datetime import datetime

class Slide(models.Model):
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

    def __unicode__(self):
        return '%s %s %s' % (self.title, self.user, self.group)

# Signals for Slide
register_signals(Slide, pre_save=signalhandlers.slide_pre_save,
                        post_save=signalhandlers.j_post_save,
                        pre_delete=signalhandlers.j_pre_delete)


class Location(models.Model):
    name = models.CharField(max_length=500)

    def __unicode__(self):
        return '%s' % self.name


class Client(models.Model):
    """Represents a Jabber client."""
    client_id = models.EmailField(max_length=128, primary_key=True)
    location = models.ForeignKey(Location, null=True, related_name='clients')
    groups = models.ManyToManyField(Group, related_name='clients')

    def all_slides(self):
        """Return all the Slides allowed."""
        slide_list = set()
        for g in self.groups.all():
            slide_list.update(g.slides.all())
        return slide_list

    def __unicode__(self):
        return '%s@%s' % (self.client_id, self.location)


class Asset(models.Model):
    UPLOAD_PATH = 'assets'

    last_update = models.DateTimeField(auto_now=True)
    file = models.FileField(upload_to=temp_upload_to)
    content_type = models.CharField(max_length=255, blank=True)
    slides = models.ManyToManyField('Slide', related_name='assets')

    def all_slides(self):
        """Returns all Slides that use this Asset."""
        return self.slides.all()

    def all_clients(self):
        """Returns all Clients that use this Asset."""
        client_list = set()
        for s in self.slides.all():
            client_list.update(s.all_clients())
        return client_list

    def url(self):
        return '%s%s' % (settings.MEDIA_URL, self.file.name)

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
            temp.save(scaffold=True)
            self.pk = temp.pk
        return self.pk

    def save(self, force_insert=False, force_update=False, scaffold=False):
        """Adds a scaffold option. When scaffold is True, the file field
        is not renamed."""
        if not scaffold:
            self._acquire_pk()

            if self.file.name:
                if not self.file.closed:
                    self.file.close()

                # Create the new directory.
                file_new_dir = self.upload_dir()
                if not path.isdir(file_new_dir):
                    os.makedirs(file_new_dir, 0755)

                # Find the new path
                file_new_path = path.join(file_new_dir,
                                          path.basename(self.file.path))

                # Move the 
                shutil.move(self.file.path, file_new_path)
                self.file = file_new_path
        
        super(self.__class__, self).save(force_insert=force_insert,
                                         force_update=force_update)


# Signals for Asset
register_signals(Asset, post_save=signalhandlers.asset_post_save,
                        pre_delete=signalhandlers.j_pre_delete)
