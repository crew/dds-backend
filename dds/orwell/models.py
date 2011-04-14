"""
Model definitions for data used by Orwell.
"""
from django.db import models
from django.contrib.auth.models import User,Group
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
import time

class RecentManager(models.Manager):
    """
    A manager for Messages that only returns messages that have been created
    within the last five minutes.
    """
    def get_query_set(self):
        """
        Returns a query set of messages within the last five minutes when this
        manager is called.
        """
        qs = super(self.__class__, self).get_query_set()
        five_minutes_ago = datetime.now() - timedelta(seconds=60 * 5)
        return qs.filter(timestamp__gt=five_minutes_ago)

# FIXME a better model than the RecentManager might be to include a "read" field
# inside Messages that Harvest can set to true once it's done with them. No need
# for a within the last 5 minutes query in that case.
class Message(models.Model):
    """
    An item in the queue intended form the Harvest service. The Message model
    and its RecentManager are used as a database-backed queue for messages to
    Harvest. When a change is made to any other model that needs to be
    communicated  to clients, a Message is made containing the needed
    data. Harvest occasionally pulls these Messages and acts on them. Messages
    usually contain json data, thus the TextField.
    """
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now=True)

    objects = models.Manager()
    recent = RecentManager()

    def tuple(self):
        return self.message, self.timestamp

    def __unicode__(self):
        return str(self.tuple())


class Slide(models.Model):
    """
    A slide that can be displayed by a client. Most of the information needed
    for a client to display a slide is held inside its bundle. This includes any
    code, images and data files. The bundle also contains a manifest file that
    includes the slide's priority, duration, title, display mode (python module
    or clutterscript layout), transition type, and thumbnail filename.

    Unfortunately, most of this information is doubled here. There was a desire
    to contain *all* the information needed to display a slide in its manifest,
    but practically, that information also needs to be in the database so that
    it can be seen by users. A method has yet to be thought of to make sure
    these two data sources remain in sync in production (as far as I know).
    """
    title = models.CharField(max_length=512)
    user = models.ForeignKey(User, related_name='slides')
    priority = models.IntegerField()
    duration = models.IntegerField(default=10)
    expires_at = models.DateTimeField(null=True, default=None, blank=True)
    last_update = models.DateTimeField(auto_now=True)
    thumbnail = models.ImageField(max_length=300, upload_to="thumbs/%Y%H%M%S",
                                  null=True)
    bundle = models.FileField(max_length=300, upload_to="slides/%Y%H%M%S",
                              null=True)

    def parse(self):
        """
        Returns slide metadata as a dictionary of its id, bundle url,
        priority, duration, and expiration date.
        """
        slide = { 'id'              : self.id,
                  'url'             : self.bundle.url,
                  'priority'        : self.priority,
                  'duration'        : self.duration,
                  'modified'        : time.mktime(self.last_update.timetuple()),
                }
        if self.expires_at:
            slide["expires_at"] = time.mktime(self.expires_at.timetuple())

        return slide

    # FIXME I don't think this is needed anymore.
    def get_class_tags(self):
        """Get a list of textual tags for this slide."""
        return ''

    def allowed(self, user):
        #FIXME! (temporary)
        return True

    @models.permalink
    def get_absolute_url(self):
        return ('orwell-slide-bundle', [str(self.id)])

    def __unicode__(self):
        return '%s %s' % (self.title, self.user)

    def thumbnailurl(self):
        return self.thumbnail.url

    def populate_from_bundle(self, bundle, tarfileobj):
        """
        Takes the metadata from the manifest file in the given bundle and
        populates this slide's files with them. The bundle is represented by
        both bundle and tarfileobj. Bundle is in a form that can be easilly
        saved to a FileField, and tarfileobj is in a form that allows easy
        access to its contained files.
        """
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
        self.bundle.save('bundle.tar.gz', bundle)
        self.save()

    def playlists(self):
        """Get the playlists associated with this slide."""
        playlists = []
        s = []
        if hasattr(self, 'playlistitem_set'):
            s += list(getattr(self, 'playlistitem_set').all())
        for playlistitem in s:
            if playlistitem.playlist not in playlists:
                playlists.append(playlistitem.playlist)
        return playlists

# Signals for Slide
register_signals(Slide, post_save=signalhandlers.slide_m_post_save,
                        pre_delete=signalhandlers.slide_m_pre_delete)


class Location(models.Model):
    """
    A possible location of a client.
    """
    name = models.CharField(max_length=500)

    def __unicode__(self):
        return '%s' % self.name


class Playlist(models.Model):
    """
    A list of slides to be displayed by a client. Each item in the list (see
    PlaylistItem) contains its position in the list and priority.
    """
    name = models.CharField(max_length=200, null=True, blank=True,
                            unique=True)

    def __unicode__(self):
        return '%s' % self.name

    @classmethod
    def get_default(cls):
        """
        Returns the default playlist for unconfigured clients. When an
        unconfigured client connects to Harvest, it is automatically assigned to
        this playlist. If the playlist doesn't alread exist, it is created.

        Note that it's up to the system administrator to make sure that the
        unconfigured clients playlist actually has a slide in it. The default
        unconfigured clients slide must be uploaded and assigned to that
        playlist.
        """
        defaultname = 'Unconfigured Clients'
        try:
            obj = cls.objects.get(name=defaultname)
        except Playlist.DoesNotExist:
            obj = cls(name=defaultname)
            obj.save()
        return obj

    def packet(self):
        """Get this playlist in dict form."""
        output = []
        for x in self.playlistitem_set.order_by('position'):
            output.append(x.subitem().asdict())
        return {'playlist':output}

    # FIXME make this name _ separated.
    def requiredslideids(self):
        """
        Returns a list of all the ids of slides needed for this playlist.
        """
        ids = []
        for x in self.playlistitem_set.order_by('position'):
            for id in x.subitem().slideids():
                if id not in ids:
                    ids.append(id)
        return ids

    def playlist_json(self):
        """
        Returns JSON for playlist editor parsing.
        """
        playlistitems = self.playlistitem_set.order_by('position')
        items = []
        # Return some simple dicts with PlaylistItem data.
        for item in playlistitems:
            item = item.subitem()
            # PlaylistItemSlide
            items.append({'type': 'PlaylistItemSlide',
                          'slide':{'id' : item.slide.id,
                                   'title' : item.slide.title,
                                   'thumbnail' : item.slide.thumbnailurl()}})
        return json.dumps(items)

    def slides(self):
        """Return all the Slide objects used in this playlist."""
        return Slide.objects.filter(id__in=self.requiredslideids())

# Signals for Playlist
register_signals(Playlist, post_save=signalhandlers.playlist_m_post_save)

class Client(models.Model):
    """Represents a DDS Jabber client."""
    name = models.CharField(max_length=100, default='Unnamed')
    client_id = models.EmailField(max_length=128, primary_key=True)
    location = models.ForeignKey(Location, null=True, related_name='clients')
    playlist = models.ForeignKey('Playlist', default=Playlist.get_default)

    def jid(self):
        """The jabber id of the client."""
        return '%s/%s' % (self.pk, settings.J_CLIENT_RESOURCE)


    def last_contact(self):
        """
        Returns the last time Harvest was in contact with this client, or None
        if there is no client activity information.
        """
        # FIXME For this and similar uses of this pattern to protect against
        # missing activity information, we should probably specifically catch
        # whatever exception is thrown when that is the case. Might hide some
        # other problem if we use a catchall.
        try:
            return self.activity.last_update
        except:
            pass

    def id_hash(self):
        """
        Returns an md5 has of this clients client_id.
        """
        hash = hashlib.md5()
        hash.update(self.client_id)
        return hash.hexdigest()

    def displayname(self):
        """
        Returns a display name for this client. If the client hasn't been named,
        the display name is the username in its client_id.

        This is used when displaying all the clients in the client index.
        """
        if self.name == 'Unnamed':
            return self.client_id.split('@')[0]
        else:
            return self.name

    def all_slides(self):
        """
        Returns all the slides that this client currently displays.
        """
        return self.playlist.slides()

    def active(self):
        """
        Returns a boolean determining whether this client is active or not. If
        there is no client activity information, returns None.
        """
        try:
            return self.activity.active
        except:
            return False

    def currentslide(self):
        """
        Returns the slide that this client is currently displaying. If there is
        no activity information for this client, returns None.
        """
        if not self.active():
            return None
        else:
            return self.activity.current_slide

    def get_class_tags(self):
        """Get a list of textual tags for this slide."""
        tags = ['client-location-%s' % self.location.id]
        if self.active():
            tags.append('client-online')
        else:
            tags.append('client-offline')
        return ' '.join(tags)

    def slideinfo(self):
        """
        Returns information used to display this slide.
        The path to this slide's current slide's thumbnail and the caption to
        use for that thumb are returned as a pair. If this client is offline,
        the path to the offline image and the caption 'Client Offline' are
        returned.
        """
        curslide = self.currentslide()
        if curslide is None:
            path = os.path.join(settings.MEDIA_URL, 'images', 'offline.png')
            caption = 'Client Offline'
        else:
            path = curslide.thumbnailurl()
            caption = curslide.title
        return path, caption

    def thumbnailurl(self):
        """
        Returns the url to the thumbnail of this client's current slide, or the
        offline image if it is offline.
        """
        return self.slideinfo()[0]

    def slidecaption(self):
        """
        Returns a caption to use for this client's thumbnail.
        """
        return self.slideinfo()[1]

    def __unicode__(self):
        return '%s@%s' % (self.pk, self.location)

# Signals for Client
register_signals(Client, post_save=signalhandlers.client_m_post_save)

class ClientActivity(models.Model):
    """
    Information about a client's activity. This keeps track of what slide a
    client is currently displaying, whether it is online or not, and the last
    time Harvest was in communication with that client. Harvest is responsible
    for updating this information.
    """
    client = models.OneToOneField(Client, primary_key=True,
                                  related_name='activity')
    current_slide = models.ForeignKey(Slide, null=True, blank=True,
                                      related_name='activities')
    active = models.BooleanField(default=False)
    last_update = models.DateTimeField(auto_now=True)

    def parse(self):
        """
        Returns dictionary representation of this client activity.
        """
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
        """
        Returns a json representation of this client activity
        """
        return json.dumps(self.parse(), default=str)

    class Meta:
        verbose_name = 'activity'
        verbose_name_plural = 'activities'

class PlaylistItem(models.Model):
    """
    An item inside a Playlist. This is meant to be more of an interface. Right
    now, playlist items only include individual Slides, but this interface
    allows for one item to represent a group of Slides or something. I'm not
    sure how useful this is, but I'll leave it for now.
    """
    position = models.PositiveIntegerField()
    playlist = models.ForeignKey(Playlist)
    slide = models.ForeignKey(Slide)

    def subitem(self):
        """
        Not sure of the utility of this, or how another playlist item
        implementation would use it..
        """
        return self

    def mode(self):
        """
        Doesn't seem very useful either..
        """
        return 'single'

    def slideids(self):
        """
        Returns a list containing the ids of slides this PlaylistItem
        represents. For this implementation, the list always has one item.
        """
        return [self.slide.id]

    def slideweights(self):
        """
        Returns a list of the priorities for the slides this PlaylistItem
        represents. The list always has one item for this implementation.
        """
        return [self.slide.priority]

    class Meta:
        unique_together = (('position', 'playlist'))

    def asdict(self):
        """
        Returns a dictionary representation of this PlaylistItem.
        """
        return {'position':self.position, 'mode':self.mode(),
                'slides':self.slideids(), 'weights':self.slideweights()}


register_signals(PlaylistItem,
                 post_save=signalhandlers.pis_m_post_save,
                 pre_delete=signalhandlers.pis_m_pre_delete)
