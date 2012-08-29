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
	def __init__(self, content=None, destination=None, origin=None, cripted=False, fingerprint=None):
		self.content = content
		self.destination = destination
		self.origin = origin
		
		self.cripted = cripted
		self.fingerprint = fingerprint
		
		self.socket = None
		
		self.__string_message = ""
		self.__dict_message = ""
		
		self.__sent_or_received = False
		
	def __decode_message(self):
		""" This function "translate" the message from string to json """
		self.__dict_message = json.loads(str(self.__string_message))
		self.origin = str(self.__dict_message['origin'])
		self.destination = str(self.__dict_message['destination'])
		self.content = str(zlib.decompress(str(self.__dict_message['content']).decode("base64")))
		
	def decode(self):
		return self.decode()
	
	def __encode_message(self):
		""" This function "translate" the message from json to string """
		self.__string_message = json.dumps(self.__dict_message)
		
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
		self.__dict_message['origin'] = str(self.origin)
		self.__dict_message['destination'] = str(self.destination)
		self.__dict_message['content'] = str(str(zlib.compress(self.content,9)).encode("base64"))
		
		self.__dict_message['hash'] = str(self.__return_hash())
				
	def sign_message(self, fingerprint):
		""" This function sign with a gpg key, the message. """
		#TODO gnupg
		return


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
		self.__decode_message()
		self.__sent_or_received = True
		
	def __get_list_splitted_message(self):
		""" This function split the message to fit the 512 bytes to send each time """	
		chunks = list()
		for i in range(0, len(self.__string_message), 512):
			chunks.append(self.__string_message[i:i+512])
		return chunks
		
	def send(self):
		""" This function send the message via the socket. """
		if self.__sent_or_received: return
		
		self.__build_message_to_send()
		self.__encode_message()
		
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		destination_dict = from_addr_to_dict(self.destination)
		
		#self.socket.connect((destination_dict['addr'], destination_dict['port']))
				
		pieces = self.__get_list_splitted_message()
		for pice in pieces:
			self.socket.sendto( pice, (destination_dict['addr'], destination_dict['port']) )
		#Message empty to stop the message
		self.socket.sendto( "", (destination_dict['addr'], destination_dict['port']) )

		data, addr = self.socket.recvfrom(512)
		if data != "OK":
			print "NOT VALID MESSAGE"
		else:
			print "Message Sent"

		self.socket.close()
		self.socket = None
		self.__sent_or_received = True
		
	def verify_gpg(self):
		""" This function verify the message with a gpg key. """
		#TODO gnupg
		return

	def is_corrupted(self):
		""" This function verify hashes to check if the message is corrupted or not """
		msg_hash = self.__return_hash()
		if self.__dict_message['hash'] == msg_hash:
			return False
		return True
		
	def __dict__(self):
		return self.__dict_message