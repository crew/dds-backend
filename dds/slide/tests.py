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
    def create_asset():
        temp = mkstemp()
        asset = Asset.objects.create(file=temp[1])
        os.close(temp[0])
        return asset

    def prepare_user_group(self):
        cls = self.__class__
        cls.u1 = User.objects.create_user('alice', 'alice@example.com')
        cls.u2 = User.objects.create_user('bob', 'bob@example.com')
        cls.u3 = User.objects.create_user('eve', 'eve@example.com')
        cls.g1 = Group.objects.create(name='Alpha')
        cls.g2 = Group.objects.create(name='Beta')
        cls.g3 = Group.objects.create(name='Gamma')
    
    @staticmethod
    def create_slide(title, priority, user, group, duration):
        return Slide.objects.create(title=title, priority=priority, user=user,
                                    group=group, duration=duration)

    def rebind(self):
        cls = self.__class__
        self.u1 = cls.u1
        self.u2 = cls.u2
        self.u3 = cls.u3
        self.g1 = cls.g1
        self.g2 = cls.g2
        self.g3 = cls.g3

        self.s1 = cls.s1
        self.s2 = cls.s2
        self.s3 = cls.s3

        self.a1 = cls.a1
        self.a2 = cls.a2
        self.a3 = cls.a3
        self.a4 = cls.a4

        self.c1 = cls.c1
        self.c2 = cls.c2

    def setUp(self):
        cls = self.__class__
        if cls.setup_called:
            self.rebind()
            return
        self.prepare_user_group()

        cls.s1 = self.create_slide('a', 1, self.u1, self.g1, 1)
        cls.s2 = self.create_slide('b', 2, self.u2, self.g2, 1)
        cls.s3 = self.create_slide('c', 3, self.u3, self.g3, 1)

        cls.a1 = self.create_asset()
        cls.a2 = self.create_asset()
        cls.a3 = self.create_asset()
        cls.a4 = self.create_asset()
        
        cls.a1.slides.add(self.s1, self.s2)
        cls.a2.slides.add(self.s1, self.s2)
        cls.a3.slides.add(self.s1)
        cls.a4.slides.add(self.s1)

        cls.a1.save()
        cls.a2.save()
        cls.a3.save()
        cls.a4.save()
    
        cls.c1 = Client.objects.create(client_id='dds@ccs', location='here')
        cls.c2 = Client.objects.create(client_id='xxx@ccs', location='there')
        
        cls.c1.groups.add(cls.g3, cls.g1)
        cls.c1.save()

        cls.c2.groups.add(cls.g1, cls.g2, cls.g3)
        cls.c2.save()
        self.rebind()
        cls.setup_called = True

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
