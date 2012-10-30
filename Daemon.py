#!/usr/bin/env python

from siderus.daemon import Handler
from time import sleep
daemon = Handler()

daemon.start()

print("Started")

while True:
    sleep(30)
    continue