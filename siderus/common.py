#!/usr/bin/python
# -*- coding=utf-8 -*-
#   Copyright 2009, 2010, 2011, 2012, 2013 Lorenzo Setale < koalalorenzo@gmail.com >

import urllib
import random
import socket

def return_myaddr():
    """ This function returns the public IP """
    if hasattr(socket, 'setdefaulttimeout'):
        socket.setdefaulttimeout(10)
    addr = urllib.urlopen('http://apps.setale.me/ip.php')    
    if hasattr(socket, 'setdefaulttimeout'):
        socket.setdefaulttimeout(None)
    return addr

def return_localip():
    """ This function returns the local IP """
    sockcon = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sockcon.connect(('www.google.com',80))
    ip, localport = sockcon.getsockname()
    sockcon.close()
    return ip

def get_random_port():
    """ This function returns a random port between 49152 and 65535 """
    random.seed()
    port = random.randint(49152, 65535) 
    return port
    
def from_addr_to_dict(address):
	"""
		This function read an address and transform it in a dictionary:
		
		>>> from_addr_to_dict("application@10.0.0.22:14916")
		{ "addr": "10.0.0.2", "port": 14916, "app": "application" } 
		
	"""
		dict_addr = dict()
		dict_addr["app"] = address[:address.index("@")]
		dict_addr["addr"] = address[address.index("@")+1:address.index(":")]
		dict_addr["port"] = int(address[address.index(":")+1:])
		
		return dict_addr
		
def from_dict_to_addr(dict_addr):
	"""
		This function read a dictionary and transform it in an address.

		The dict_addr MUST be filled like this:		
		{ "addr": "10.0.0.2", "port": 14916, "app": "application" }
	"""
		return "%s:%s:%s" % ( dict_addr['app'], dict_addr['addr'], dict_addr['port'] )

