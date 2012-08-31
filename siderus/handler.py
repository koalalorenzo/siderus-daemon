#!/usr/bin/env python
# -*- coding=utf-8 -*-
#   Copyright 2009, 2010, 2011, 2012, 2013 Lorenzo Setale < koalalorenzo@gmail.com >

from siderus.message import Message

from siderus.common import from_dict_to_addr
from siderus.common import from_addr_to_dict
from siderus.common import return_network_publicip
from siderus.common import is_local_address

class DaemonHandler(object):
	"""	
		This class manage the connections between nodes. The properties 
		of the node are saved and managed by this class. It should save
		configurations and gpg keys in a database. 
		It include a message cache to send messages to the 
		local-destination even if the  applicationis no reachable (Ex:
		the app is not open and is not listening, but the message is 
		saved and sent when it will be available ).
	"""
	def __init__(self):
		self.connections = list()
		self.message_cache = list()
		self.applications = list()
		
	def analyze(self, message):
		""" This function decode and analyze the message. """
		message.decode()
		destination = from_addr_to_dict(message.destination)
		if destination['app'] == "daemon":
			if is_local_address(message.destination):
				#do applications and connections stuff
			else:
				#accept connections
		else:
			#forward message to the application
		return
		
	def listen_loop(self):
		""" This function run a infinite loop that get messages. """
		while 1:
			message = Message()
			message.receive()
			#thread this process:
			self.analyze(message)
	