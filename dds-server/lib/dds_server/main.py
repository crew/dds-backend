# ***** BEGIN LICENCE BLOCK *****
#
# The Initial Developer of the Original Code is
# The Northeastern University CCIS Volunteer Systems Group
# 
# Contributor(s):
#   Alex Lee <lee@ccs.neu.edu>
#
# ***** END LICENCE BLOCK *****
import sys
import logging
import xmpp
import gflags as flags
from daemonize import daemonize
from handler import DDSHandler

flags.DEFINE_string('config_file', '/etc/dds-server.conf',
                    'Path to the configuration file')
flags.DEFINE_string('config_section', 'DEFAULT',
                    'Configuration file section to parse')
flags.DEFINE_string('log_file', None, 'Log file path')
flags.DEFINE_boolean('debug', False, 'Enable debugging')
flags.DEFINE_boolean('daemonize', True, 'Enable Daemon Mode')

FLAGS = flags.FLAGS


def parse_config():
    import ConfigParser
    config = ConfigParser.RawConfigParser()
    config.read(FLAGS.config_file)
    return [ config.get(FLAGS.config_section, 'username'),
             config.get(FLAGS.config_section, 'password'),
             config.get(FLAGS.config_section, 'resource'),
             config.get(FLAGS.config_section, 'server'),
             config.get(FLAGS.config_section, 'log'),
             config.getboolean(FLAGS.config_section, 'debug'), ]


def get_options():
    all_list = parse_config()

    if FLAGS.log_file:
        all_list[4] = FLAGS.log_file

    if FLAGS.debug:
        all_list[5] = FLAGS.debug

    return all_list


def alive(dispatch):
    try:
        dispatch.Process(1)
    except:
        logging.info('Connection closed.')
        return False
    return True


def main():
    (username, password, resource, server, log, debug) = get_options()
    handler = DDSHandler()

    if FLAGS.daemonize:
        daemonize()

    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s %(message)s',
                        filename=log,
                        filemode='a')

    if debug:
        client = xmpp.Client(server=server)
    else:
        client = xmpp.Client(server=server, debug=[])
    try:
        client.connect()
    except:
        logging.debug('Connecting to server failed.')
        exit()

    try:
        client.auth(username, password, resource, sasl=False)
    except:
        logging.debug('Authorization failed.')
        exit()

    client.RegisterHandler('presence', handler.presence_handle)
    client.RegisterHandler('iq', handler.iq_handle, ns=xmpp.NS_RPC)
    client.sendInitPresence()

    logging.info('Connection started')

    while alive(client):
        pass
