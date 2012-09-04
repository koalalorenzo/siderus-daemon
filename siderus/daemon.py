#!/usr/bin/env python
# -*- coding=utf-8 -*-
#   Copyright 2009, 2010, 2011, 2012, 2013 Lorenzo Setale < koalalorenzo@gmail.com >

from siderus.message import Message

from siderus.common import from_dict_to_addr
from siderus.common import from_addr_to_dict
from siderus.common import from_arg_to_addr
from siderus.common import return_my_daemon_address
from siderus.common import is_local_address
from siderus.common import get_random_port

DAEMON_NODE_CONN_REQ     = 0
DAEMON_NODE_CONN_REF     = 1
DAEMON_NODE_CONN_SHR_ASK = 2
DAEMON_NODE_CONN_SHR_ANS = 3

DAEMON_APP_CONN_REQ      = 4 # Req keys: Node
DAEMON_APP_CONN_REF      = 5 # Req keys: Node
DAEMON_APP_CONN_LST_ASK  = 6 
DAEMON_APP_CONN_LST_ANS  = 7 
DAEMON_APP_CONN_SHR_ASK  = 8 # Req keys: Node
DAEMON_APP_LCCN_REQ      = 9
DAEMON_APP_LCCN_REQ_PRT  = 10
DAEMON_APP_LCCN_REF      = 11


class Handler(object):
	"""	
		This class manage the connections between nodes. The properties 
		of the node are saved and managed by this class. It should save
		configurations and gpg keys in a database. 
		It include a message cache to send messages to the 
		local-destination even if the  applicationis no reachable (Ex:
		the app is not open and is not listening, but the message is 
		saved and sent when it will be available ).
	"""
	def __init__(self, address=None):
		self.connections = list()
		self.messages_cache = list() #TODO: load it from database
		self.applications = dict() # { 'app': 123 }
		
		if address:
			self.address = address
		else: 
			self.address = return_my_daemon_address()
			
	def connect(self, address):
		""" This function send a connection request to a specific address """
		if address in self.connections: return
		
		message = Message(destination=address, origin=self.address)
		message.content = {"intent": DAEMON_NODE_CONN_REQ}
		message.send()
				
	def disconnect(self, address):
		""" This function send a disconnection request to a node """
		if not address in self.connections: return
		
		message = Message(destination=address, origin=self.address)
		message.content = {"intent": DAEMON_NODE_CONN_REF}
		message.send()
		self.connections.pop(self.connections.index(daemon_address))
		
	def ask_connections(self, address):
		""" This functions "share" connections with another node """
		
		message = Message(destination=address, origin=self.address)
		message.content = { "intent": DAEMON_NODE_CONN_SHR_ASK }
		message.send()
		
	def send_connections(self, address):
		""" This functions "share" connections with another node """
		
		message = Message(destination=address, origin=self.address)
		message.content = {
							"intent": DAEMON_NODE_CONN_SHR_ANS, 
							"connections": self.connections
						  }
		message.send()

	def __connect_to_nodes(self, nodes):
		for node in nodes:
			self.connect(node)
	
	def __analyze_message_from_remote_app(self, message):
		ip_address = from_dict_to_addr(message.origin)['addr'] 
		daemon_address = return_daemon_address(ip_address)

		if message.content['intent'] == DAEMON_NODE_CONN_REQ:
			self.connect(daemon_address)
			self.connections.append(daemon_address)

		elif message.content['intent'] == DAEMON_NODE_CONN_REF:
			self.connections.pop(self.connections.index(daemon_address))
		
		elif message.content['intent'] == DAEMON_NODE_CONN_SHR_ASK:
			self.send_connections(daemon_address)
		
		elif message.content['intent'] == DAEMON_NODE_CONN_SHR_ANS:
			self.__connect_to_nodes(message.content['connections'])
		
		else:
			print "What are you doing? -", message.content
			
		return
	
	def add_application(self, application):
		""" 
			This function send to the application the port 
			to use establishing a connection.
		"""	
		port = get_random_port(exclude_list=self.applications.values())
		dest = from_arg_to_addr(application, "127.0.0.1", 52225)
		
		message = Message(destination=dest, origin=orig)
		message.content = {"intent": DAEMON_APP_LCCN_REQ_PRT, "port": port}
		message.send()
				
		self.applications[application] = port
		
	def __send_app_connections(self, app):
		if not app in self.applications.keys(): return
		
		dest = from_arg_to_addr(app, "127.0.0.1", self.applications[app])
		orig = from_arg_to_addr()
		
		message = Message(destination=dest, origin=orig)
		message.content = {
							"intent": DAEMON_APP_CONN_LST_ANS, 
							"connections": self.connections
						   }
		message.send()
		
	def __analyze_message_from_local_app(self, message):
		# Requestes arrived from local applications, es: list connections, connect, disconnect
		application = from_dict_to_addr(message.origin)['app'] 

		if message.content['intent'] == DAEMON_APP_LCCN_REQ:
			self.add_application(application)
			return
		if not application in self.applications: return
		
		if message.content['intent'] == DAEMON_APP_LCCN_REF:
			self.appliations.pop(application)
			
		elif message.content['intent'] == DAEMON_APP_CONN_REQ:
			self.connect(message.content['node'])
			
		elif message.content['intent'] == DAEMON_APP_CONN_REF:
			self.disconnect(message.content['node'])
			
		elif message.content['intent'] == DAEMON_APP_CONN_LST_ASK:
			self.__send_app_connections(application)
			
		elif message.content['intent'] == DAEMON_APP_CONN_SHR_ASK:
			self.ask_connections(message.content['node'])
		return
		
	def __forward_message(self, received_message):
		connection = return_daemon_address_by_giving_address(received_message.origin)
		if not connection in self.connections:
			return
			
		destination_dict = from_addr_to_dict(received_message.destination)
		
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
			self.__forward_message(message)
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
	