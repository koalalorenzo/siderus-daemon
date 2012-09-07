#!/usr/bin/python
# -*- coding=utf-8 -*-
#   Copyright 2009, 2010, 2011, 2012, 2013 Lorenzo Setale < koalalorenzo@gmail.com >

import urllib
import random
import socket

# Constants

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

DEFAULT_SEND_MESSAGE_TIMEOUT  = 15

# Coommon functions

def return_network_publicip():
	""" This function returns the public IP """
	if hasattr(socket, 'setdefaulttimeout'):
		socket.setdefaulttimeout(10)
	addr = urllib.urlopen('http://apps.setale.me/ip.php').read()
	if hasattr(socket, 'setdefaulttimeout'):
		socket.setdefaulttimeout(None)
	return addr

def return_subnet_localip():
	""" This function returns the local IP """
	sockcon = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sockcon.connect(('www.google.com',80))
	ip, localport = sockcon.getsockname()
	sockcon.close()
	return ip
	
def get_random_port(exclude_list=None):
	""" This function returns a random port between 49152 and 65535 """
	random.seed()
	port = random.randint(49152, 65535)
	if exclude_list:
		if int(port) in exclude_list: return get_random_port()
	if int(port) is 52125: return get_random_port()
	return int(port)
	
def from_addr_to_dict(address):
	"""
		This function read an address and transform it in a dictionary:
		
		>>> from_addr_to_dict("application@10.0.0.22:52125")
		{ "addr": "10.0.0.2", "port": 52125, "app": "application" } 
		
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
		{ "addr": "10.0.0.2", "port": 52125, "app": "application" }
	"""
	return "%s@%s:%s" % ( dict_addr['app'], dict_addr['addr'], dict_addr['port'] )

def from_arg_to_addr(app="daemon", addr="127.0.0.1", port=52125):
	""" This function return a Siderus address by passing its data as options. """	
	return "%s@%s:%s" % ( app, addr, port )

def is_subnet_address(raw_address):
	""" This function returns True if the address is pointing to a node in subnet """
	addr_dict = from_addr_to_dict(raw_address)
	if "10.0" in addr_dict['addr']: return True
	if "192.168" in addr_dict['addr']: return True
	return False

def is_local_address(raw_address):
	""" This function returns True if the address is pointing to localhost """
	addr_dict = from_addr_to_dict(raw_address)
	if "localhost" in addr_dict['addr']: return True
	if "127.0.0.1" in addr_dict['addr']: return True
	return False
	
def is_addressed_to_daemon(raw_address):
	""" This function check if the raw_address is pointing to a daemon"""
	addr_dict = from_addr_to_dict(raw_address)
	if addr_dict["app"] == "daemon": return True
	return False
	
def return_daemon_address(ip_address):
	""" This function returns the raw address of a specific daemon """
	
	dict_addr = dict()
	dict_addr["app"] = "daemon"
	dict_addr["addr"] = ip_address
	dict_addr["port"] = 52125
	
	return from_dict_to_addr(dict_addr)
	
def return_my_daemon_address(public=True):
	""" This function return the daemon address. """
	if public:
		address = return_network_publicip()
	else:
		address = return_subnet_localip()
	return return_daemon_address(address)
	
def return_daemon_address_by_giving_address(address):
	""" This functions return the daemon address by giving a Siderus address. """
	
	dict_addr = from_addr_to_dict(address)
	dict_addr["app"] = "daemon"
	dict_addr["port"] = 52125
	
	return from_dict_to_addr(dict_addr)
	
def return_application_address(application, port):
	""" This function returns the application correct address by giving its name and port """
	
	dict_addr = dict()
	dict_addr["addr"] = return_network_publicip()
	dict_addr["app"] = application
	dict_addr["port"] = int(port)
	
	return from_dict_to_addr(dict_addr)
	
	