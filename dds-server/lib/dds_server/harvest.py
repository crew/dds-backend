# vim: set shiftwidth=4 tabstop=4 softtabstop=4 expandtab :

import threading
import time
import json
import logging
import dblayer
from dblayer import generate_request
from handler import DDSHandler


class Combine(threading.Thread):
    """You know, like a farm?"""

    def __init__(self, jabber, timeout=10, **kwargs):
        self.jabber = jabber
        self.timeout = 10
        super(self.__class__, self).__init__(**kwargs)

    def collect(self):
        for m in dblayer.collect_messages():
            logging.debug(str(m))
            try:
                self.send_message(m)
            except KeyError, e:
                logging.error('Failed to parse.')
            except Exception, e:
                logging.error(str(e))
            # The message is deleted.
            m.delete()

    def send_message(self, message):
        obj = json.loads(message.message)
        # Get the slide.
        slide = dblayer.get_slide(obj['slide'])
        # Get the recipient
        if obj.has_key('to'):
            tos = [obj['to']]
        elif slide:
            tos = [c.jid() for c in slide.all_clients()]
        if slide is None:
            # Mocking.
            slide = object()
            slide.pk = obj['slide']
            slide.parse = lambda: slide.pk
        # Determine the request
        if obj['method'] == 'add':
            request = generate_request((slide.parse(), ), methodname='addSlide')
        elif obj['method'] == 'delete':
            request = generate_request((slide.pk, ), methodname='removeSlide')
        # Send.
        logging.info('Sending...')
        for to in tos:
            logging.info('Sending to %s' % to)
            self.jabber.send(DDSHandler.get_iq(to, 'set', request))
        logging.info('Done.')

    def run(self):
        while True:
            self.collect()
            time.sleep(self.timeout)