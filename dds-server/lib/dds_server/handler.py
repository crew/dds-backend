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

from dds.slide.models import Client, Slide
from dds.utils import generate_request


class DDSHandler(object):

    def presence_handle(self, dispatch, pr):
        """If a client sends presence, send its initial slides."""
        try:
            jid = pr.getFrom()
            typ = pr.getType()
            logging.debug('%s : got presence.' % jid)
            if ((typ != 'unavailable') and
                pr.getStatus() == 'initialsliderequest'):
                self.send_initial_slides(dispatch, jid)
            else:
                logging.info('%s : has gone offline.' % jid)
        except Exception, e:
            logging.error('%s' % e)
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

    def send_initial_slides(self, dispatch, jid):
        """Sends the initial slides to the Jabber id."""
        logging.info('%s : sending initial slides.' % jid)
        for slide in self.get_slides_for(jid.getStripped()):
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

    def get_slides_for(self, jid):
        """Return a list of the Slide objects for the Client with the given
        Jabber id."""
        c = self.get_client(jid)
        if c is None:
            return []
        return c.all_slides()

    def get_client(self, jid):
        """ Gets the Client from Django, if one exists. """
        logging.debug('%s : looking for client in the database.' % jid)
        try:
            c = Client.objects.get(pk=jid)
        except:
            logging.debug('%s : client is not found.' % jid)
            return None
        return c