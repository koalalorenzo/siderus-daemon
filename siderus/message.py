#!/usr/bin/python
# -*- coding=utf-8 -*-
#   Copyright 2009, 2010, 2011, 2012, 2013 Lorenzo Setale < koalalorenzo@gmail.com >

import socket
import json
import zlib
from hashlib import md5
import os

from siderus.common import from_addr_to_dict
from siderus.common import is_local_address

class Message(object):
	""" 
		This is the message class that receives and sends the message.
		Each message is a json dictionary, sometimes it is encrypted for security reasons.
	"""
	def __init__(self, content=None, destination=None, origin=None):
		self.content = content
		self.destination = destination
		self.origin = origin

		self.__hash = None
		self.socket = None
		
		self.__string_message = ""
		self.__dict_message = dict()
		
		self.__sent_or_received = False
		
	def decode(self):
		""" This function "translate" the message from string to json """
		self.__dict_message = json.loads(str(self.__string_message))
		self.origin = str(self.__dict_message['origin'])
		self.destination = str(self.__dict_message['destination'])
		self.content = json.loads(str(zlib.decompress(str(self.__dict_message['content']).decode("base64"))))
		
		# With SIDERUS_DEBUG=1 it will print stuff
		if os.environ.has_key('SIDERUS_DEBUG') and bool(int(os.environ['SIDERUS_DEBUG'])):
			print "R:", self.content

	def __build_message_to_send(self):
		""" This function build the self.__dict_message to send """
		if not self.content: return
		if not self.destination: return
		if not self.origin: return 
		
		self.__dict_message = dict()
		self.__dict_message['origin'] = str(self.origin)
		self.__dict_message['destination'] = str(self.destination)
		self.__dict_message['content'] = str(str(zlib.compress(json.dumps(self.content),9)).encode("base64"))
		
		self.__dict_message['hash'] = str(self.hash())
		
	def encode_message(self):
		""" This function "translate" the message from json to string """
		self.__build_message_to_send()
		self.__string_message = json.dumps(self.__dict_message)
		
	def hash(self):
		""" this function returns the hash to verify the content integrity """
		if not self.__hash:
			hashobj = md5(json.dumps(self.content))
			self.__hash = str(hashobj.hexdigest())
		return self.__hash
		
	def receive(self):
		""" This function receive the message via the socket but do not decode it """
		if self.__sent_or_received: return
		
		port = from_addr_to_dict(self.destination)['port']
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		
		cache = ""
		
		self.socket.bind(('', port))
		#self.socket.listen(1)
		
		#second, addr = self.socket.accept()
		#These function should be executed in a different thread!
		while True:
			#data = second.recv(512)
			data, addrport = self.socket.recvfrom(512)
			if not data: break
			cache += data
		self.socket.sendto("OK", addrport)
		
		self.__string_message = cache
		self.socket.close()
		self.socket = None
	
	def receive_and_decode(self):
		""" This function receive the message via socket and decode it """
		self.receive()
		self.decode()
		self.__sent_or_received = True
		
	def __get_list_splitted_message(self):
		""" This function split the message to fit the 512 bytes to send each time """	
		chunks = list()
		for i in range(0, len(self.__string_message), 512):
			chunks.append(self.__string_message[i:i+512])
		return chunks
		
	def send(self):
		""" This function send the message via the socket. """
		if self.__sent_or_received: return #RAISE
		
		self.encode_message()
		
		# With SIDERUS_DEBUG=1 it will print stuff
		if os.environ.has_key('SIDERUS_DEBUG') and bool(int(os.environ['SIDERUS_DEBUG'])):
			print "S:", self.content

		self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		destination_dict = from_addr_to_dict(self.destination)

		if not is_local_address(self.destination):
			# If the destination is remote, send it to the Daemon
			destination_dict['port'] = 52125 
			
		pieces = self.__get_list_splitted_message()
		for pice in pieces:
			self.socket.sendto( pice, (destination_dict['addr'], destination_dict['port']) )
		#Message empty to stop it
		self.socket.sendto( "", (destination_dict['addr'], destination_dict['port']) )

		data, addr = self.socket.recvfrom(512)
		if data != "OK":
			return # RAISE 

		self.socket.close()
		self.socket = None
		self.__sent_or_received = True
		
	def is_corrupted(self):
		""" This function verify hashes to check if the message is corrupted or not """
		msg_hash = self.hash()
		if self.__dict_message['hash'] == msg_hash:
			return False
		return True
		
	def __dict__(self):
		return self.__dict_message
		
	def __str__(self):
		return self.__string_message
	
	def __unicode__(self):
		return u"%s" % self.__string_message

	def __eq__(self, other):
		if other.hash() == self.hash():
			return True
		return False
		
	def __ne__(self, other):
		return not self.__eq__(other)