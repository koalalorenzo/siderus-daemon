#!/usr/bin/env python
# -*- coding=utf-8 -*-
#   Copyright 2009, 2010, 2011, 2012, 2013 Lorenzo Setale < koalalorenzo@gmail.com >

from siderus.message import Message

from siderus.common import DAEMON_APP_CONN_REQ
from siderus.common import DAEMON_APP_CONN_REF
from siderus.common import DAEMON_APP_CONN_LST_ASK
from siderus.common import DAEMON_APP_CONN_LST_ANS 
from siderus.common import DAEMON_APP_CONN_SHR_ASK
from siderus.common import DAEMON_APP_LCCN_REQ
from siderus.common import DAEMON_APP_LCCN_REQ_PRT
from siderus.common import DAEMON_APP_LCCN_REF

from siderus.common import from_arg_to_addr
from siderus.common import return_daemon_address

class Handler(object):
	def __init__(self, name):
		if not name: return # TODO: ERROR! 
		self.name = name
		self.address = None
		
		# This is used by threads to send message "sequentially"
		self.__messages_queque = list() 

		self.__register_app()

	def __register_app(self):
		""" This function ask the Siderus Daemon to register the app """
		
		self.address = from_arg_to_addr(app=self.name, port=52225) #TMP addr
		daemon_address = return_daemon_address("127.0.0.1")
		
		message_ask = Message(origin=self.address, destination=daemon_address)
		message_ask.content = {"intent": DAEMON_APP_LCCN_REQ}
		message_ask.send()

		message_port = Message(destination=self.address)
		message_port.receive_and_decode()
		
		self.address = message_port.content['address']		
		
	def __listen_loop(self):
		""" This function run a infinite loop that get messages. """
		if not self.address: return 
		while True:
			message = Message()
			message.receive()
			#thread:
			message.decode()
			print(message.content)