# Siderus
Siderus is project that aim to create a peer-to-peer network made by applications. It works with a few libraries and a daemon to help developers to make python applications p2p without efforts.

This project and the code is in pre-alpha and is not usable right now.

## Main Features
* It works both on IPv4 and IPv6 connections
* NAT-PMP support to "avoid" firewall automatically.
* Siderus speak json!
* Encoding used is UTF-8
* Messages are crypted and compressed!
* OpenVPN support
* Friend-To-Friend network support
* Integrated cache for messages ( Siderus works off-line )
* ...and more to come! :D 

## How it works
Each node in the network has installed the Siderus daemon. It is a program that works 
in background to manage connections. It receives and sends messages with other nodes 
and applications. It could be considered as a 
"[Mercury]( http://en.wikipedia.org/wiki/Mercury_%28mythology%29 )" :D. Locally, each daemon 
is connected to some applications. An application receives messages directly from the daemon.

When a message arrives from another node, it is first received by the daemon. The daemon verifies the message and the origin, then sends it to the specific application addressed. This happens also when an application has to send a message: messages to send are collected by the daemon, and then are sent to the remote destination/node.


## License

This work is licensed under a Creative Commons Attribution-NonCommercial-NoDerivs 3.0 Unported License. To view a copy of this license, visit [http://creativecommons.org/licenses/by-nc-nd/3.0/]( http://creativecommons.org/licenses/by-nc-nd/3.0/ ) .