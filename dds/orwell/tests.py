"""
Tests for Orwell's models and views.
"""
from models import *
from datetime import datetime
from django.contrib.auth.models import User
from django.test import TestCase
from datetime import datetime, timedelta

class OrwellTest(TestCase):
    """
    The base class form tests on Orwell. Sets up fixtures.
    """
    def setUp(self):
        self.alice = User.objects.create_user("alice", "alice@example.com", "foo")
        self.bob = User.objects.create_user("bob", "bob@example.com", "foo")
        self.eve = User.objects.create_user("eve", "eve@example.com", "foo")

        self.a = Slide.objects.create(title="a", priority=1, user=self.alice)
        self.b = Slide.objects.create(title="b", priority=2, user=self.bob)
        self.c = Slide.objects.create(title="c", priority=3, user=self.eve)
        self.d = Slide.objects.create(title="d", priority=4, user=self.alice)

        self.first_pl = Playlist.objects.create(name="First")
        PlaylistItem.objects.create(position=1, playlist=self.first_pl, slide=self.a)
        PlaylistItem.objects.create(position=2, playlist=self.first_pl, slide=self.b)
        PlaylistItem.objects.create(position=3, playlist=self.first_pl, slide=self.d)
        self.second_pl = Playlist.objects.create(name="Second")
        PlaylistItem.objects.create(position=1, playlist=self.second_pl, slide=self.c)
        PlaylistItem.objects.create(position=2, playlist=self.second_pl, slide=self.a)

        self.here = Location.objects.create(name='here')
        self.there = Location.objects.create(name='there')

        self.dds = Client.objects.create(client_id='dds@ccs',
                                         location=self.here,
                                         playlist=self.first_pl)
        self.xxx = Client.objects.create(client_id='xxx@ccs',
                                         location=self.there,
                                         playlist=self.second_pl)

    def assertSetEquals(self, first, second, msg=None):
        self.assertEquals(set(first), set(second), msg=msg)

class MessageModelTests(OrwellTest):
    """
    Tests for the Message model.
    """
    def test_recent_manager(self):
        """
        Tests the Message model's RecentManager. Make sure it only returns
        Messages created recently.
        """
        # Note, setting the timestamp for an individual Message doesn't work
        # here, because of the auto_now=True declaration in that Field. Whenever
        # a Message is created or saved, timestamp is automatically set to
        # datetime.now(). QuerySet.update() bypasses that mechanism though, so I
        # use it here.
        message = Message.objects.create()
        Message.objects.update(timestamp=datetime.now() - timedelta(days=1))
        self.failUnlessEqual(Message.recent.count(), 0)
        message = Message.objects.create()
        self.failUnlessEqual(Message.recent.filter(id=message.id).count(), 1)

class SlideModelTests(OrwellTest):
    """
    Tests for the Slide model.
    """
    def test_playlists(self):
        """
        Tests the slide.playlists() method.
        """
        self.assertSetEquals(self.a.playlists(), [self.first_pl, self.second_pl])
        self.assertSetEquals(self.c.playlists(), [self.second_pl])

class ClientModelTests(OrwellTest):
    """
    Tests for the Client model.
    """
    def test_client_all_slides(self):
        """
        Tests the client.all_slides() method.
        """
        self.assertSetEquals(self.dds.all_slides(), [self.a, self.b, self.d])
        self.assertSetEquals(self.xxx.all_slides(), [self.c, self.a])
