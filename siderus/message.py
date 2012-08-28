#!/usr/bin/python
# -*- coding=utf-8 -*-
#   Copyright 2009, 2010, 2011, 2012, 2013 Lorenzo Setale < koalalorenzo@gmail.com >

import socket
import json
import zlib
from hashlib import md5

from siderus.common import from_dict_to_addr
from siderus.common import from_addr_to_dict
from siderus.common import return_myaddr
from siderus.common import is_local_address

class Message(object):
	""" 
		This is the message class that receives and sends the message.
		Each message is a json dictionary, sometimes it is encrypted for security reasons.
	"""
	def __init__(content=None, destination=None, origin=None, cripted=False, fingerprint=None):
		self.content = content
		self.destination = destination
		self.origin = origin
		
		self.cripted = cripted
		self.fingerprint = fingerprint
		
		#self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #TCP connection
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #UDP connection
		
		self.__string_message = ""
		self.__dict_message = ""
		
	def __decode_message(self):
		""" This function "translate" the message from string to json """
		if self.__dict_message: return
		if not self.__string_message: return
		
		self.__dict_message = json.loads(self.__string_message)
		self.origin = self.__dict_message['origin']
		self.destination = self.__dict_message['destination']
		self.content = zlib.decompress(str(self.__dict_message['content']).decode("base64"))
		
	def __encode_message(self):
		""" This function "translate" the message from json to string """
		if self.__string_message: return
		if not self.__dict_message: return
		
		self.__string_message = json.loads(self.__dict_message)
		
	def __return_hash(self):
		""" this function returns the hash to verify the content integrity """
		hash = md5(self.content)
		return str(hash.hexdigest())

	def __build_message_to_send(self):
		""" This function build the self.__dict_message to send """
		if not self.content: return
		if not self.destination: return
		if not self.origin: return 
		
		self.__dict_message = dict()
		self.__dict_message['origin'] = self.origin
		self.__dict_message['destination'] = self.destination
		self.__dict_message['content'] = str(zlib.compress(content,9)).encode("base64")
		
		self.__dict_message['hash'] = self.__return_hash()
				
	def sign_message(self, fingerprint):
		""" This function sign with a gpg key, the message. """
		#TODO
		return


	def receive(self):
		""" This function receive the message via the socket. """
		port = from_addr_to_dict(self.destination)['port']
		
		self.__string_message = ""
		
		self.socket.bind(('', port))
		self.socket.listen(1)
		
		second, addr = self.socket.accept()
		#These function should be executed in a different thread!
		while True:
			data = second.recv(512)
			if not data: break
	        self.__string_message += data

		self.__decode_message()
		
	def send(self):
		""" This function send the message via the socket. """
		return

		
	def verify_gpg(self):
		""" This function verify the message with a gpg key. """
		#TODO
		return
