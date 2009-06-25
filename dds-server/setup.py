#!/usr/bin/env python

from distutils.core import setup

# FIXME version number, etc.
setup(
    name = 'dds-server',
    description = 'Digital Display Jabber Server',
    author = 'Alex Lee',
    author_email = 'lee@ccs.neu.edu',
    maintainer = 'Alex Lee',
    maintainer_email = 'lee@ccs.neu.edu',
    scripts = ['scripts/dds-server'],
    packages = ['dds', 'dds.slide'],
    package_dir = {'' : 'lib'},
    data_files = [('/etc', ['cfg/dds-server.conf']),],
)
