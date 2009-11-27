# vim: set shiftwidth=4 tabstop=4 softtabstop=4 expandtab :
# ***** BEGIN LICENCE BLOCK *****
#
# The Initial Developer of the Original Code is
# The Northeastern University CCIS Volunteer Systems Group
#
# Contributor(s):
#   Alex Lee <lee@ccs.neu.edu>
#
# ***** END LICENCE BLOCK *****
import os
import sys
import logging
import xmpp
import gflags as flags
from daemonize import daemonize
from harvest import Combine

flags.DEFINE_string('config_file', '/etc/dds-server.conf',
                    'Path to the configuration file')
flags.DEFINE_string('config_section', 'DEFAULT',
                    'Configuration file section to parse')
flags.DEFINE_string('log_file', None, 'Log file path')
flags.DEFINE_boolean('debug', False, 'Enable debugging')
flags.DEFINE_boolean('daemonize', True, 'Enable Daemon Mode')
flags.DEFINE_string('dds_path', '/', 'Path to the dds module.')
FLAGS = flags.FLAGS


def parse_config():
    import ConfigParser
    config = ConfigParser.RawConfigParser()
    config.read(FLAGS.config_file)
    return [config.get(FLAGS.config_section, 'username'),
            config.get(FLAGS.config_section, 'password'),
            config.get(FLAGS.config_section, 'resource'),
            config.get(FLAGS.config_section, 'server'),
            config.get(FLAGS.config_section, 'log'),
            config.getboolean(FLAGS.config_section, 'debug'),
            config.get(FLAGS.config_section, 'dds-path'), ]


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
    except Exception, e:
        logging.error(str(e))
        logging.info('Connection closed.')
        return False
    return True


def main():
    (username, password, resource, server, log, debug, path) = get_options()
    # Delayed import because the path is not set before this point.
    sys.path.insert(0, path)
    try:
        from handler import DDSHandler
        handler = DDSHandler()
    except ImportError:
        logging.critical('The path to DDS is not set.')
        sys.stderr.write('The dds module is not found.\n')
        os.exit(1)

    if FLAGS.daemonize:
        daemonize()

    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(filename)s %(lineno)s '
                               '%(levelname)s %(message)s',
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
        os.exit(2)

    try:
        client.auth(username, password, resource, sasl=False)
    except:
        logging.debug('Authorization failed.')
        os.exit(3)

    # Register the handlers.
    client.RegisterHandler('presence', handler.presence_handle)
    client.RegisterHandler('iq', handler.iq_handle, ns=xmpp.NS_RPC)
    client.sendInitPresence()

    logging.info('Connection started')

    combine = Combine(client, timeout=10)
    combine.daemon = True
    combine.start() # wrrrrrrr

    while alive(client):
        pass
