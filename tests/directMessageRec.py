#!/usr/bin/env python

import sys
sys.path.append("..")
sys.path.append("../..")

from siderus.message import Message
from siderus.common import return_application_address, from_arg_to_addr

destination = return_application_address("MessageTester" , 52225)

m = Message(destination=destination)
m.receive_and_decode()

print(m.content)