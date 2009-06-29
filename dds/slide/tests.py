import unittest
import os
from tempfile import mkstemp
from models import *
from datetime import datetime
from django.contrib.auth.models import User, Group


class SlideTestCase(unittest.TestCase):
    setup_called = False

    def assertSetEquals(self, first, second, msg=None):
        self.assertEquals(set(first), set(second), msg=msg)

    @staticmethod
    def create_asset(pk):
        asset, _ = Asset.objects.get_or_create(pk=pk)
        return asset

    @staticmethod
    def create_user(name, email):
        user, _ = User.objects.get_or_create(username=name, email=email)
        return user

    @staticmethod
    def create_group(name):
        group, _ = Group.objects.get_or_create(name=name)
        return group

    @staticmethod
    def create_slide(title, priority, user, group, duration):
        slide, _ = Slide.objects.get_or_create(title=title, priority=priority,
                                               user=user, group=group,
                                               duration=duration)
        return slide

    def setUp(self):
        self.u1 = self.create_user('alice', 'alice@example.com')
        self.u2 = self.create_user('bob', 'bob@example.com')
        self.u3 = self.create_user('eve', 'eve@example.com')
        self.g1 = self.create_group('Alpha')
        self.g2 = self.create_group('Beta')
        self.g3 = self.create_group('Gamma')

        self.s1 = self.create_slide('a', 1, self.u1, self.g1, 1)
        self.s2 = self.create_slide('b', 2, self.u2, self.g2, 1)
        self.s3 = self.create_slide('c', 3, self.u3, self.g3, 1)

        self.a1 = self.create_asset(100)
        self.a2 = self.create_asset(200)
        self.a3 = self.create_asset(300)
        self.a4 = self.create_asset(400)

        self.a1.slides.add(self.s1, self.s2)
        self.a2.slides.add(self.s1, self.s2)
        self.a3.slides.add(self.s1)
        self.a4.slides.add(self.s1)

        self.a1.save()
        self.a2.save()
        self.a3.save()
        self.a4.save()

        self.l1, _ = Location.objects.get_or_create(name='here')
        self.l2, _ = Location.objects.get_or_create(name='there')

        self.c1, _ = Client.objects.get_or_create(client_id='dds@ccs',
                                                  location=self.l1)
        self.c2, _ = Client.objects.get_or_create(client_id='xxx@ccs',
                                                  location=self.l2)

        self.c1.groups.add(self.g3, self.g1)
        self.c1.save()

        self.c2.groups.add(self.g1, self.g2, self.g3)
        self.c2.save()

    def testslideFindAssets(self):
        self.assertSetEquals(self.s1.all_assets(),
                             [self.a1, self.a2, self.a3, self.a4])
        self.assertSetEquals(self.s2.all_assets(), [self.a1, self.a2])
        self.assertSetEquals(self.s3.all_assets(), [])

    def testSliceslideFindClients(self):
        self.assertSetEquals(self.s1.all_clients(), [self.c1, self.c2])
        self.assertSetEquals(self.s2.all_clients(), [self.c2])
        self.assertSetEquals(self.s3.all_clients(), [self.c1, self.c2])

    def testclientFindSlides(self):
        self.assertSetEquals(self.c1.all_slides(), [self.s1, self.s3])
        self.assertSetEquals(self.c2.all_slides(), [self.s1, self.s2, self.s3])

    def testassetFindSlides(self):
        self.assertSetEquals(self.a1.all_slides(), [self.s1, self.s2])
        self.assertSetEquals(self.a2.all_slides(), [self.s1, self.s2])
        self.assertSetEquals(self.a3.all_slides(), [self.s1])
        self.assertSetEquals(self.a4.all_slides(), [self.s1])

    def testassetFindClients(self):
        self.assertSetEquals(self.a1.all_clients(), [self.c1, self.c2])
        self.assertSetEquals(self.a2.all_clients(), [self.c1, self.c2])
        self.assertSetEquals(self.a3.all_clients(), [self.c1, self.c2])
        self.assertSetEquals(self.a4.all_clients(), [self.c1, self.c2])
