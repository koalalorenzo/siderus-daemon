#!/usr/bin/python
# -*- coding=utf-8 -*-
#   Copyright 2009, 2010, 2011, 2012, 2013 Lorenzo Setale < koalalorenzo@gmail.com >

import socket
import json

class Message(object):
	""" 
		This is the message class that receives and sends the message.
		Each message is a json dictionary, sometimes it is encrypted for security reasons.
	"""
	def __init__(content=None, destination=None):
		self.content = content
		self.destination = destination
		
		self.__fingerprint = None
		self.__hash_md5 = None
		
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.__raw_message = ""
		self.__encoded_message = ""

		self.origin = None
		
    def __encode_message(self):
		return
		
	def __decode_message(self):
		return
		
	def sign_message(self, fingerprint):
		""" This function sign with a gpg key, the message. """
		return
		
	def verify_gpg(self):
		""" This function verify the message with a gpg key. """
		
    def receive(self):
    	""" This function receive the message via the socket. """
    	return
    	
    def send(self):
	    """ This function send the message via the socket. """
	    return
