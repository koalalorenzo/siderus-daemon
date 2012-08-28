#!/usr/bin/env python
# -*- coding=utf-8 -*-
#   Copyright 2009, 2010, 2011, 2012, 2013 Lorenzo Setale < koalalorenzo@gmail.com >

from siderus.message import Message

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
	def __init__():
		self.connections = list()
		self.message_cache = list()
		self.applications = list()
		
	def analyze(self, message):
		return
		
	def listen_loop(self):
		while 1:
			message = Message()
			message.receive()
			#thread this process:
			self.analyze(message)
		