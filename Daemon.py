#!/usr/bin/env python

from siderus.daemon import Handler
from time import sleep
daemon = Handler(port=12345)

daemon.start()

print("Started")

while True:
    sleep(30)
    continue