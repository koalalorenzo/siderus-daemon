#!/usr/bin/env python
# -*- coding=utf-8 -*-
#   Copyright 2009, 2010, 2011, 2012, 2013 Lorenzo Setale < koalalorenzo@gmail.com >

from siderus.message import Message

from siderus.common import from_dict_to_addr
from siderus.common import from_addr_to_dict
from siderus.common import return_network_publicip
from siderus.common import is_local_address

DAEMON_REM_CONN_REQ     = 0
DAEMON_REM_CONN_REF     = 1
DAEMON_REM_CONN_SHR_ASK = 2
DAEMON_REM_CONN_SHR_GOT = 3

DAEMON_LOC_CONN_REQ     = 0
DAEMON_LOC_CONN_REF     = 1

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
		self.messages_cache = list() #TODO: load it from database
		self.applications_ports = dict() # { 'app': 123 }
		
	def __analyze_message_from_local_app(self, message):
		return
		
	def __analyze_message_from_remote_app(self, message):
		return
		
	def __forward_message(self, received_message):
		destination_dict = from_addr_to_dict(message.destination)

		if destination_dict['app'] in self.applications.keys():
			destination_dict['port'] = int(self.applications[destination_dict['app']])
		else:
			# If app "installed" but not active: cache the forwarded message!
			return
		
		destination_dict['addr'] = "127.0.0.1"
		new_destination = from_dict_to_addr(destination_dict)
		forward = Message()
		forward.content = received_message.content
		forward.origin = received_message.origin
		forward.destination = new_destination
		
		#if app is listening then send. Otherwise cache the message.
		forward.send()
		
	def analyze(self, message):
		""" This function decode and analyze the message. """
		message.decode()

		if message.is_corrupted():
			#reply with a new "error" message with the sent message.__hash.
			return

		destination = from_addr_to_dict(message.destination)
		if destination['app'] == "daemon":
			if is_local_address(message.destination): 
				self.__analyze_message_from_local_app(message)
				return
			else:
				self.__analyze_message_from_remote_app(message)
				return
		else:
			print
			#forward message to the application
		return
		
	def listen_loop(self):
		""" This function run a infinite loop that get messages. """
		while 1:
			message = Message()
			message.receive()
			#thread this process:
			self.analyze(message)
			
			
	def clear_cache(self):
		""" This function sends all the message saved in the cache. """
		for message in self.messages_cache:
			message.send()
	