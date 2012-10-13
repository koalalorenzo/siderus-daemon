#!/usr/bin/env python
# -*- coding=utf-8 -*-
#   Copyright 2009, 2010, 2011, 2012, 2013 Lorenzo Setale < koalalorenzo@gmail.com >

import pybonjour
import select
import socket

from thread import start_new_thread as thread
from time import sleep

from siderus.message import Message

from siderus.common import return_my_daemons_addresses
from siderus.common import return_networks_addresses
from siderus.common import from_dict_to_addr
from siderus.common import from_addr_to_dict
from siderus.common import from_arg_to_addr
from siderus.common import return_my_daemon_address
from siderus.common import is_local_address
from siderus.common import get_random_port
from siderus.common import return_daemon_address
from siderus.common import return_application_address
from siderus.common import is_addr_in_network

# Import remote intents:
from siderus.common import DAEMON_NODE_CONN_REQ
from siderus.common import DAEMON_NODE_CONN_REF
from siderus.common import DAEMON_NODE_CONN_SHR_ASK
from siderus.common import DAEMON_NODE_CONN_SHR_ANS
from siderus.common import DAEMON_NODE_CONN_CHK

# Import local intents:
from siderus.common import DAEMON_APP_CONN_REQ
from siderus.common import DAEMON_APP_CONN_REF
from siderus.common import DAEMON_APP_CONN_LST_ASK
from siderus.common import DAEMON_APP_CONN_LST_ANS 
from siderus.common import DAEMON_APP_CONN_SHR_ASK
from siderus.common import DAEMON_APP_LCCN_REQ
from siderus.common import DAEMON_APP_LCCN_REQ_PRT
from siderus.common import DAEMON_APP_LCCN_REF

# Time stuff
from siderus.common import DEFAULT_DAEMON_CHECK_ALIVE_NODES

class AutodiscoverService(object):
	"""
		This class manage the local-connections with other peers, 
		discovering it by bonjour/avahi ( Zeroconf-like network ).
	"""
	def __init__(self):
		self.nodes = list()
		self.active = True
		
	def register(self):
		service = pybonjour.DNSServiceRegister(name="Siderus", regtype="_siderus._udp", port=52125)
		while 1:
			pybonjour.DNSServiceProcessResult(service)
			if not self.active:
				service.close()		
					

	def __query_record_callback(self, sdRef, flags, interfaceIndex, errorCode, fullname,
							  rrtype, rrclass, rdata, ttl):
		""" 
			This "private" function manage the callback from pybonjour.
			Code modified from pybonjour example.
		"""
		if errorCode == pybonjour.kDNSServiceErr_NoError:
			addr = socket.inet_ntoa(rdata)
			if not addr in self.nodes:
				self.nodes.append(addr)
	
	def __resolve_callback(self, sdRef, flags, interfaceIndex, errorCode, fullname,
						 hosttarget, port, txtRecord):
		""" 
			This "private" function manage the callback from pybonjour.
			Code modified from pybonjour example.
		"""
		if errorCode != pybonjour.kDNSServiceErr_NoError:
			return
		query_sdRef = pybonjour.DNSServiceQueryRecord(interfaceIndex=interfaceIndex,
											fullname=hosttarget,
											rrtype=pybonjour.kDNSServiceType_A,
											callBack=self.__query_record_callback)
	
		try:
			while True:
				if not self.active: break
				ready = select.select([query_sdRef], [], [], 5)
				if query_sdRef not in ready[0]:
					break
				pybonjour.DNSServiceProcessResult(query_sdRef)
			else:
				queried.pop()
		finally:
			query_sdRef.close()
						
	def __browse_callback(self, sdRef, flags, interfaceIndex, errorCode, serviceName, regtype, replyDomain):
		""" 
			This "private" function manage the callback from pybonjour.
			Code modified from pybonjour example.
		"""
		if errorCode != pybonjour.kDNSServiceErr_NoError: return
		resolve_sdRef = pybonjour.DNSServiceResolve(0,
													interfaceIndex,
													serviceName,
													regtype,
													replyDomain,
													self.__resolve_callback)
		try:
			while True:
				if not self.active: break
				ready = select.select([resolve_sdRef], [], [], 5)
				if resolve_sdRef not in ready[0]:
					break
				pybonjour.DNSServiceProcessResult(resolve_sdRef)
			else:
				resolved.pop()
		finally:
			resolve_sdRef.close()
			
	def discover(self):
		"""
			This function discover the other nodes/peers and
			add them in self.nodes.
		"""
		browse_sdRef = pybonjour.DNSServiceBrowse(regtype="_siderus._udp",
												  callBack=self.__browse_callback)
		
		try:
			while True:
				if not self.active: break
				ready = select.select([browse_sdRef], [], [])
				if browse_sdRef in ready[0]:
					pybonjour.DNSServiceProcessResult(browse_sdRef)
		finally:
			browse_sdRef.close()
			
	def discover_thread(self):
		""" This function start self.discover in a different thread """
		thread(self.discover, () )	
		
	def register_thread(self):
		""" This function start self.register in a different thread """
		thread(self.register, () )	
	
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
		

		self.addresses = return_my_daemons_addresses()
		self.networks = return_networks_addresses()
		
		self.__bonjour_active = False
		self.__bonjour_discover = None
		self.__listening = False
		
	def __return_origin_to_use(self, address):
		""" This function return the correct origin to use in the message """
		for network in self.networks:
			if is_addr_in_network(address, network):
				addr = self.networks[network]['addr']
				return return_daemon_address(addr)
		raise Exception("NoDaemonAddress for '%s'" % address)
				
	def connect(self, address):
		""" This function send a connection request to a specific address """
		if address in self.connections: return
		
		daemon_address = self.__return_origin_to_use(address)
				
		message = Message(destination=address, origin=daemon_address)
		message.content = {"intent": DAEMON_NODE_CONN_REQ}
		message.send()		
				
	def disconnect(self, address):
		""" This function send a disconnection request to a node """
		if not address in self.connections: return

		self.connections.pop(self.connections.index(address))

		daemon_address = self.__return_origin_to_use(address)
				
		message = Message(destination=address, origin=daemon_address)
		message.content = {"intent": DAEMON_NODE_CONN_REF}
		try:
			message.send()
		except:
			# The message is not received, so the connection will drop.
			pass
		
	def is_node_alive(self, address):
		""" This function check if the connection is still alive """
		if not address in self.connections: return
		
		daemon_address = self.__return_origin_to_use(address)
				
		message = Message(destination=address, origin=daemon_address)
		message.content = {"intent": DAEMON_NODE_CONN_CHK}
		try:
			message.send()
		except:
			return False
		return True

	def __zeroconf_nodes_autoconnect(self):
		while 1:
			if not self.__bonjour_active: 
				self.__bonjour_discover.active = False
				break
			sleep(1)
			for node in self.__bonjour_discover.nodes:
				address = return_daemon_address(node)
				if address in self.addresses: continue
				if address in self.connections: continue
				self.connect(address)
		return
	
	def start_zeroconf(self):
		""" 
			This function start two bonjour-thread to connect automatically 
			to the nearby devices
		"""
		if self.__bonjour_active: return
		
		self.__bonjour_active = True
		self.__bonjour_discover = AutodiscoverService()
		self.__bonjour_discover.register_thread()
		self.__bonjour_discover.discover_thread()
		thread(self.__zeroconf_nodes_autoconnect, () )
		
	def ask_connections(self, address):
		""" This functions "share" connections with another node """
		
		daemon_address = self.__return_origin_to_use(address)
		
		message = Message(destination=address, origin=daemon_address)
		message.content = { "intent": DAEMON_NODE_CONN_SHR_ASK }
		message.send()
		
	def send_connections(self, address):
		""" This functions "share" connections with another node """
		daemon_address = self.__return_origin_to_use(address)
		
		message = Message(destination=address, origin=daemon_address)
		message.content = {
							"intent": DAEMON_NODE_CONN_SHR_ANS, 
							"connections": self.connections
						  }
		message.send()

	def __connect_to_nodes(self, nodes):
		for node in nodes:
			self.connect(node)
	
	def __analyze_message_from_remote_app(self, message):
		ip_address = from_addr_to_dict(message.origin)['addr'] 
		daemon_address = return_daemon_address(ip_address)

		if message.content['intent'] == DAEMON_NODE_CONN_REQ:
			if daemon_address in self.connections: return
			self.connect(daemon_address)
			self.connections.append(daemon_address)
		
		elif message.content['intent'] == DAEMON_NODE_CONN_REF:
			self.connections.pop(self.connections.index(daemon_address))
		
		elif message.content['intent'] == DAEMON_NODE_CONN_SHR_ASK:
			self.send_connections(daemon_address)
		
		elif message.content['intent'] == DAEMON_NODE_CONN_SHR_ANS:
			self.__connect_to_nodes(message.content['connections'])
		elif message.content['intent'] == DAEMON_NODE_CONN_CHK:
			return # Do Nothing...
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
		orig = return_daemon_address("127.0.0.1")
		app_address = return_application_address(application, port)
		
		message = Message(destination=dest, origin=orig)
		message.content = {"intent": DAEMON_APP_LCCN_REQ_PRT, "address": app_address }
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
		application = from_addr_to_dict(message.origin)['app'] 

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
		
	def __listen_loop(self):
		""" This function run a infinite loop that get messages. """
		while 1:
			if not self.__listening: break
			message = Message(destination="@:52125")
			message.receive()
			thread(self.analyze, (message,) )
		return
		
	def __connection_check_loop(self):
		""" 
			This function checks every %s seconds 
			if every nodes/connections are alive. If not, it will disconnect from them.
		""" % DEFAULT_DAEMON_CHECK_ALIVE_NODES
		while 1:
			if not self.__listening: break
			sleep(DEFAULT_DAEMON_CHECK_ALIVE_NODES)
			for address in self.connections:
				if not self.is_node_alive(address):
					thread(self.disconnect, (address, ))
		return
		
	def clear_cache(self):
		""" This function sends all the message saved in the cache. """
		for message in self.messages_cache:
			message.send()
	
	def start(self):
		""" This function starts the daemon in threads """
		if self.__listening: raise Exception("Daemon Already Started")
		self.__listening = True
		
		thread(self.__connection_check_loop, () )
		thread(self.__listen_loop, () )
		self.start_zeroconf()
		
	def stop(self):
		""" This function stops the daemon threads """
		self.__bonjour_active = False
		if self.__bonjour_discover:
			self.__bonjour_discover.active = False
		for address in self.connections:
			thread(self.disconnect, (address,))
		sleep(1)
		self.__listening = False
		