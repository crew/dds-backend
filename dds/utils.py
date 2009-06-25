# ***** BEGIN LICENCE BLOCK *****
#
# The Initial Developer of the Original Code is
# The Northeastern University CCIS Volunteer Systems Group
#
# Contributor(s):
#   Alex Lee <lee@ccs.neu.edu>
#
# ***** END LICENCE BLOCK *****

import xmpp
import xmlrpclib
import os
from os import path


def module(file_path):
    """Returns the module name.
    >>> module('/a/b/c/xx.py')
    'c'
    """
    dir = path.dirname(file_path)
    dir_abs = path.abspath(dir)
    dir_norm = path.normpath(dir_abs)
    return dir_norm.split(os.sep)[-1]


def root(file_path):
    """Returns a 'lambda' that produces paths based on the given file_path.
    >>> x = root('/a/b/c/xx.py')
    >>> x('t')
    '/a/b/c/t'
    >>> x('t', 's')
    '/a/b/c/t/s'
    """
    dir = path.dirname(file_path)
    normpath = path.normpath
    join = path.join
    return (lambda *base: normpath(join(dir, *base)).replace('\\', '/'))


def generate_request(variables, methodname=None, methodresponse=None,
                     encoding='utf-8', allow_none=False):
    """Create an xml format of the varibles and the methodname if given."""
    request = xmlrpclib.dumps(variables, methodname, methodresponse, encoding,
                              allow_none)
    return [xmpp.simplexml.NodeBuilder(request).getDom()]


class JabberClientWrapper(object):
    """A wrapper for xmpp.Client"""
    _client = None

    def __init__(self, username='', password='', resource='', server='',
                 port=5222, proxy=None, ssl=None, use_srv=True, debug=[]):
        if self.__class__._client:
            self.client = self.__class__._client
            self.refresh()
            return

        self.__class__._client = xmpp.Client(server, port, debug)
        self.client = self.__class__._client
        self.client.connect(proxy=proxy, secure=ssl, use_srv=use_srv)
        if self.client.isConnected():
            self.client.auth(username, password, resource)
            self.client.sendInitPresence(requestRoster=1)

    def refresh(self):
        if not self.client.isConnected():
            self.client.reconnectAndReauth()

    def send_model(self, jid, model, function):
        """Sends a django model with the function name."""
        m = model.__class__.objects.values().get(pk=model.pk)
        request = generate_request((m, ), function)
        self.send_request(jid, request)

    def send_parsed_model(self, jid, parsed_model, function):
        """Send a django model, but parse it with the given function, the
        parser should return a tuple."""
        request = generate_request(parsed_model, function)
        self.send_request(jid, request)

    def send_request(self, jid, request, typ = 'set'):
        """Send the given request over Jabber. The request must be an xml
        node."""
        iq = xmpp.Iq(to = jid, typ = typ)
        iq.setQueryNS(xmpp.NS_RPC)
        iq.setQueryPayload(request)
        self.client.send(iq)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
