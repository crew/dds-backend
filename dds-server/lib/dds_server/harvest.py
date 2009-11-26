# vim: set shiftwidth=4 tabstop=4 softtabstop=4 expandtab :

import threading
import time
import os
import json
import dblayer

class Combine(threading.Thread):

    def collect(self):
        for m in collect_messages():
            message, timestamp = m.tuple()
            try:
                print json.loads(message), timestamp
            except:
                print 'Eeeee'

    def run(self):
        while True:
            self.collect()
            time.sleep(10)
