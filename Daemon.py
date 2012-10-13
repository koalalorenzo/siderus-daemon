#!/usr/bin/env python

from siderus.daemon import Handler

daemon = Handler()

daemon.start()

print("Started")

while True:
    continue