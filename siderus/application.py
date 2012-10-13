#!/usr/bin/env python
# -*- coding=utf-8 -*-
#   Copyright 2009, 2010, 2011, 2012, 2013 Lorenzo Setale < koalalorenzo@gmail.com >

from thread import start_new_thread as thread

from siderus.message import Message

from siderus.common import DAEMON_APP_NAME
from siderus.common import DAEMON_APP_PORT
from siderus.common import DEFAULT_APP_TMP_PORT

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
		
		# This is used by threads to send/get message "sequentially" in buffer
		self.__messages_outqueque = list() 
		self.__messages_in_queque = list() 

		self.__register_app()

	def __register_app(self):
		""" This function ask the Siderus Daemon to register the app """
		
		self.address = from_arg_to_addr(app=self.name, port=DEFAULT_APP_TMP_PORT)
		daemon_address = return_daemon_address("127.0.0.1")
		
		message_ask = Message(origin=self.address, destination=daemon_address)
		message_ask.content = {"intent": DAEMON_APP_LCCN_REQ}
		
		message_port = Message(destination=self.address)
		
		message_ask.send()
		message_port.receive_and_decode()
		
		self.address = message_port.content['address']		
		
	def __decode_and_buffer_message(self, message):
		message.decode()
		self.__messages_in_queque.append(message)
		
	def __listen_loop(self):
		""" This function run a infinite loop that get messages. """
		if not self.address: return 
		while True:
			message = Message()
			message.receive()
			thread( self.__decode_and_buffer_message, (message,) )
		