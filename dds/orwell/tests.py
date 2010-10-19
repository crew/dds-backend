import unittest
import os
from tempfile import mkstemp
from models import *
from datetime import datetime
from django.contrib.auth.models import User


class SlideTestCase(unittest.TestCase):
    setup_called = False

    def assertSetEquals(self, first, second, msg=None):
        self.assertEquals(set(first), set(second), msg=msg)

    @staticmethod
    def create_user(name, email):
        user, _ = User.objects.get_or_create(username=name, email=email)
        return user

    @staticmethod
    def create_slide(title, priority, user, duration):
        slide, _ = Slide.objects.get_or_create(title=title, priority=priority,
                                               user=user,
                                               duration=duration)
        return slide

    def setUp(self):
        self.u1 = self.create_user('alice', 'alice@example.com')
        self.u2 = self.create_user('bob', 'bob@example.com')
        self.u3 = self.create_user('eve', 'eve@example.com')

        self.s1 = self.create_slide('a', 1, self.u1, 1)
        self.s2 = self.create_slide('b', 2, self.u2, 1)
        self.s3 = self.create_slide('c', 3, self.u3, 1)

        self.l1, _ = Location.objects.get_or_create(name='here')
        self.l2, _ = Location.objects.get_or_create(name='there')

        self.c1, _ = Client.objects.get_or_create(client_id='dds@ccs',
                                                  location=self.l1)
        self.c2, _ = Client.objects.get_or_create(client_id='xxx@ccs',
                                                  location=self.l2)

        self.c1.save()

        self.c2.save()

    def testSliceslideFindClients(self):
        self.assertSetEquals(self.s1.all_clients(), [self.c1, self.c2])
        self.assertSetEquals(self.s2.all_clients(), [self.c2])
        self.assertSetEquals(self.s3.all_clients(), [self.c1, self.c2])

    def testclientFindSlides(self):
        self.assertSetEquals(self.c1.all_slides(), [self.s1, self.s3])
        self.assertSetEquals(self.c2.all_slides(), [self.s1, self.s2, self.s3])
