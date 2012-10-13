#!/usr/bin/env python

import sys
sys.path.append("..")
sys.path.append("../..")

from siderus.message import Message
from siderus.common import return_application_address, from_arg_to_addr
import sys

destination = from_arg_to_addr(app="MessageTester", addr=sys.argv[1], port=52225)
origin = return_application_address("MessageTester", 52225)

m = Message(" ".join(sys.argv[2:]), destination, origin)
m.send()