# vim: set tabstop=4 softtabstop=4 shiftwidth=4 expandtab :
"""DDS XMPP Server Executable.

***** BEGIN LICENCE BLOCK *****

The Initial Developer of the Original Code is
The Northeastern University CCIS Volunteer Systems Group

Contributor(s):
  Alex Lee <lee@ccs.neu.edu>

***** END LICENCE BLOCK *****
"""

__author__ = 'Alex Lee <lee@ccs.neu.edu>'

import xmlrpclib
import xmpp
import logging
import dblayer
from dblayer import generate_request


class DDSHandler(object):

    def presence_handle(self, dispatch, pr):
        """If a client sends presence, send its initial slides."""
        jid = pr.getFrom()
        jidto = pr.getTo()
        if jid.getStripped() == jidto.getStripped():
            logging.debug('Skipping message from self')
            return
        typ = pr.getType()
        logging.debug('%s : got presence. %s' % (jid, jidto))

        client = None

        logging.debug('%s : looking for client in the database.' % jid)
        jid_stripped = jid.getStripped()
        client, client_created = dblayer.get_client(jid_stripped)
        activity, activity_created = dblayer.get_activity(jid_stripped)

        if client_created:
            logging.debug('%s : registered previously unseen client' % jid)
        if activity_created:
            logging.info("No client activity for this client")
            self.presence_handle(dispatch, pr)

        if client:
            if (pr.getStatus() == 'initialsliderequest'):
                self.send_initial_slides(dispatch, jid, client.all_slides())
            ca = client.activity
            ca.active = (typ != 'unavailable')
            ca.current_slide = dblayer.get_slide(pr.getStatus())
            ca.save()
            if not ca.active:
                logging.info('%s : has gone offline.' % jid)
        raise xmpp.NodeProcessed

    def iq_handle(self, dispatch, iq):
        jid = iq.getFrom()
        iq_type = iq.getType()
        ns = iq.getQueryNS()

        logging.debug('%s : got IQ' % jid)
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

    @classmethod
    def get_iq(cls, jid, typ, request):
        iq = xmpp.Iq(to=jid, typ=typ)
        iq.setQueryNS(xmpp.NS_RPC)
        iq.setQueryPayload(request)
        return iq

    def add_slide(self, dispatch, jid, slide, method_name='addSlide'):
        """Sends a parsed Slide object to the Jabber id."""
        logging.info('%s : sending slide %d.' % (jid, slide.pk))
        request = generate_request(slide.parse(), methodname=method_name)
        dispatch.send(self.get_iq(jid, 'set', request))
        logging.info('%s : sent slide %d.' % (jid, slide.pk))

    def send_error(self, dispatch, jid, payload=('error', )):
        """Sends an error."""
        logging.info('%s : sending error' % jid)
        request = generate_request(payload)
        dispatch.send(self.get_iq(jid, 'error', request))
        logging.info('%s : sent error' % jid)
