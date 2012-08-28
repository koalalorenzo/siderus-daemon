#!/usr/bin/env python
# -*- coding=utf-8 -*-
#   Copyright 2009, 2010, 2011, 2012, 2013 Lorenzo Setale < koalalorenzo@gmail.com >

class Application(object):
	""" 
		This class allows applications to connect to the Handler 
		to send and receive messages.
	"""
	def __init__(self, name):
		self.name = name
		self.internal_port = 0 # Port defined by the Handler