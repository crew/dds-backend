"""DDS XMPP Server Executable.

***** BEGIN LICENCE BLOCK *****

The Initial Developer of the Original Code is
The Northeastern University CCIS Volunteer Systems Group

Contributor(s):
  Alex Lee <lee@ccs.neu.edu>

***** END LICENCE BLOCK *****
"""

import xmlrpclib
import xmpp
import logging
import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'dds.settings'
from django.core.exceptions import ObjectDoesNotExist
from dds.orwell.models import Client, ClientActivity, Slide, Location
from django.contrib.auth.models import Group
from dds.utils import generate_request


class DDSHandler(object):

    def presence_handle(self, dispatch, pr):
        """If a client sends presence, send its initial slides."""
        jid = pr.getFrom()
        typ = pr.getType()
        logging.debug('%s : got presence.' % jid)

        try:
            client = self.get_client(jid.getStripped())
            if client:
                client_activity = client.activity
                if (typ == 'unavailable'):
                    logging.info('%s : has gone offline.' % jid)
                    client_activity.active = False
                    client_activity.current_slide = None
                elif (pr.getStatus() == 'initialsliderequest'):
                    self.send_initial_slides(dispatch, jid, client.all_slides())
                    client_activity.active = True
                else:
                    try:
                      slide_id = int(pr.getStatus())
                      curslide = Slide.objects.get(pk=slide_id)
                      client_activity.current_slide = curslide
                    except:
                      logging.exception('Error setting current slide')
                client_activity.save()
        except ObjectDoesNotExist, e:
            logging.info("No client activity for this client")
            client = self.get_client(jid.getStripped())
            client_activity = ClientActivity(client=client)
            client_activity.save()
            self.presence_handle(dispatch, pr)
        except Exception, e:
            logging.exception('Exception while setting presence')
        raise xmpp.NodeProcessed

    def iq_handle(self, dispatch, iq):
        jid = iq.getFrom()
        iq_type = iq.getType()
        ns = iq.getQueryNS()

        logging.debug('Got IQ from %s' % jid)
        if not jid:
            logging.debug('No jid')
            raise xmpp.NodeProcessed

        if iq_type == 'get':
            request = xmlrpclib.loads(str(iq))
            method_name = request[1]

            if method_name == 'getSlide':
                try:
                    self.get_slide(dispatch, iq)
                except Exception, e:
                    self.send_error(dispatch, jid)
                    logging.error('%s : %s' % (jid, e))

            raise xmpp.NodeProcessed

    def get_slide(self, dispatch, iq):
        # Sample method call:
        #
        # <methodCall>
        #   <methodName>getSlide</methodName>
        #   <params>
        #     <param>
        #       <value><int>1</int></value>
        #     </param>
        #   </params>
        # </methodCall>
        jid = iq.getFrom()
        reply = iq.buildReply(typ='result')
        reply.setQueryNS(iq.getQueryNS())

        # parse the xml find the slide
        request = xmlrpclib.loads(str(iq))
        slide_id = request[0][0]
        slide = Slide.objects.get(pk=slide_id)

        # Check ACL
        client = self.get_client(jid.getStripped())
        if (client is None) or (client not in slide.all_clients()):
            raise Exception('%s is not allowed.' % jid)

        # Prepare the result
        result = xmlrpclib.dumps(slide.parse())
        payload = [xmpp.simplexml.NodeBuilder(result).getDom()]
        reply.setQueryPayload(payload)
        logging.info('%s : sending getSlide %d reply.' % (jid, slide.pk))
        dispatch.send(reply)
        logging.info('%s : sent getSlide %d reply.' % (jid, slide.pk))

    def send_initial_slides(self, dispatch, jid, slides):
        """Sends the initial slides to the Jabber id."""
        logging.info('%s : sending initial slides.' % jid)
        for slide in slides:
            self.add_slide(dispatch, jid, slide)
        else:
            # The client is unregistered, send it a slide to that effect
            # TODO: Make this happen
            pass

    def add_slide(self, dispatch, jid, slide, method_name='addSlide'):
        """Sends a parsed Slide object to the Jabber id."""
        logging.info('%s : sending slide %d.' % (jid, slide.pk))
        request = generate_request(slide.parse(), methodname=method_name)

        iq = xmpp.Iq(to=jid, typ='set')
        iq.setQueryNS(xmpp.NS_RPC)
        iq.setQueryPayload(request)

        dispatch.send(iq)
        logging.info('%s : sent slide %d.' % (jid, slide.pk))

    def send_error(self, dispatch, jid, payload=('error',)):
        """Sends an error."""
        logging.info('%s : sending error' % jid)
        request = generate_request(payload)

        iq = xmpp.Iq(to=jid, typ='error')
        iq.setQueryNS(xmpp.NS_RPC)
        iq.setQueryPayload(request)

        dispatch.send(iq)
        logging.info('%s : sent error' % jid)

    def get_client(self, jid):
        """ Gets the Client from Django, if one exists. """
        logging.debug('%s : looking for client in the database.' % jid)
        try:
            c, created = Client.objects.get_or_create(pk=jid)
        except:
            logging.debug('%s : client is not found.' % jid)
            return None
        if created:
            logging.debug('%s : registering previously unseen client' % jid)
            location, loc_created = Location.objects.get_or_create(name='Unknown')
            c.location = location
            group, group_created = Group.objects.get_or_create(name='Unregistered clients')
            c.groups.add(group)
            c.save()
        return c
