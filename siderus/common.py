#!/usr/bin/python
# -*- coding=utf-8 -*-
#   Copyright 2009, 2010, 2011, 2012, 2013 Lorenzo Setale < koalalorenzo@gmail.com >

import urllib
import random
import socket
import netifaces
import netaddr

# Constants

DAEMON_APP_NAME = "daemon"
DAEMON_APP_PORT = 52125

DAEMON_NODE_CONN_REQ     = 1.1
DAEMON_NODE_CONN_REF     = 1.2
DAEMON_NODE_CONN_SHR_ASK = 2.1
DAEMON_NODE_CONN_SHR_ANS = 2.2
DAEMON_NODE_CONN_CHK     = 3

DAEMON_APP_CONN_REQ      = 4.1 # Req keys: Node
DAEMON_APP_CONN_REF      = 4.2 # Req keys: Node
DAEMON_APP_CONN_LST_ASK  = 5.1 
DAEMON_APP_CONN_LST_ANS  = 5.2 
DAEMON_APP_CONN_SHR_ASK  = 6 # Req keys: Node
DAEMON_APP_LCCN_REQ      = 7.1
DAEMON_APP_LCCN_REQ_PRT  = 7.2
DAEMON_APP_LCCN_REF      = 7.3

DEFAULT_SEND_MESSAGE_TIMEOUT     = 10
DEFAULT_DAEMON_CHECK_ALIVE_NODES = 15

DEFAULT_APP_TMP_PORT =  52225

# Coommon functions

def return_network_publicip():
	""" This function returns the public IP """
	if hasattr(socket, 'setdefaulttimeout'):
		socket.setdefaulttimeout(10)
	addr = urllib.urlopen('http://apps.setale.me/ip.php').read()
	if hasattr(socket, 'setdefaulttimeout'):
		socket.setdefaulttimeout(None)
	return addr

def return_addresses():
	""" This function returns all the addresses of the  """
	addresses = list()
	interfaces = netifaces.interfaces()
	for interface in interfaces:
		points = netifaces.ifaddresses(interface)
		for key in points.keys():
			for data in points[key]:
				if data.has_key('addr'):
					addresses.append(data['addr'])
	return addresses
	
def return_networks_addresses():
	""" This function returns a dict containing the addresses fore each network """
	networks = dict()
	interfaces = netifaces.interfaces()

	for interface in interfaces:
		points = netifaces.ifaddresses(interface)
		for key in points.keys():
			for data in points[key]:
				if not data.has_key('netmask'):
					continue
				netmask = data['netmask']
				addr = data['addr']
				try:
					cidr = netaddr.IPNetwork('%s/%s' % (addr, netmask))
					network = cidr.network
				except:
					continue
				key = "%s/%s" % (str(network), netmask)
				networks[key] = dict()
				networks[key]['addr'] = addr
				networks[key]['netmask'] = netmask

	return networks
	
def get_random_port(exclude_list=None):
	""" This function returns a random port between 49152 and 65535 """
	random.seed()
	port = random.randint(49152, 65535)
	if exclude_list:
		if int(port) in exclude_list: return get_random_port()
	if int(port) is DAEMON_APP_PORT: return get_random_port()
	return int(port)
	
def from_addr_to_dict(address):
	"""
		This function read an address and transform it in a dictionary:
		
		>>> from_addr_to_dict("application@10.0.0.22:DAEMON_APP_PORT")
		{ "addr": "10.0.0.2", "port": DAEMON_APP_PORT, "app": "application" } 
		
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
		{ "addr": "10.0.0.2", "port": DAEMON_APP_PORT, "app": "application" }
	"""
	return "%s@%s:%s" % ( dict_addr['app'], dict_addr['addr'], dict_addr['port'] )

def from_arg_to_addr(app="daemon", addr="127.0.0.1", port=DAEMON_APP_PORT):
	""" This function return a Siderus address by passing its data as options. """	
	return "%s@%s:%s" % ( app, addr, port )

def is_siderus_address(raw_address):
	""" This function returns True if the given string is a siderus address"""
	try:
		from_addr_to_dict(raw_address)
		return True
	except:
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
	if addr_dict["app"] == DAEMON_APP_NAME: return True
	return False
	
def return_daemon_address(ip_address):
	""" This function returns the raw address of a specific daemon """
	
	dict_addr = dict()
	dict_addr["app"] = DAEMON_APP_NAME
	dict_addr["addr"] = ip_address
	dict_addr["port"] = DAEMON_APP_PORT
	
	return from_dict_to_addr(dict_addr)
	
def return_my_daemons_addresses():
	""" This function returns the daemon addresses. """
	addresses = list()
	for addr in return_addresses():
		addresses.append(return_daemon_address(addr))
	return addresses
	
def return_my_daemon_address(public=True):
	""" This function returns the daemon address. """
	address = return_network_publicip()
	return return_daemon_address(address)
	
def return_daemon_address_by_giving_address(address):
	""" This functions return the daemon address by giving a Siderus address. """
	
	dict_addr = from_addr_to_dict(address)
	dict_addr["app"] = DAEMON_APP_NAME
	dict_addr["port"] = DAEMON_APP_PORT
	
	return from_dict_to_addr(dict_addr)
	
def return_application_address(application, port):
	""" This function returns the application correct address by giving its name and port """
	
	dict_addr = dict()
	dict_addr["addr"] = return_network_publicip()
	dict_addr["app"] = application
	dict_addr["port"] = int(port)
	
	return from_dict_to_addr(dict_addr)
	
def return_all_my_daemon_addresses():
	""" This function returns all the possible daemon addresses """
	addrs = return_addresses()
	addresses = list()
	for ip in addrs:
		addresses.append(return_daemon_address(ip))
	return addresses
	
def is_addr_in_network(addr, network):
	""" This function check if the first IP is a specific network"""
	if is_siderus_address(addr):
		addr = from_addr_to_dict(addr)['addr']
	return netaddr.IPAddress(addr) in netaddr.IPNetwork(network).cidr

	