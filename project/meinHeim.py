#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import string

import cherrypy
from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_remote_switch import BrickletRemoteSwitch

#global variables
tinkerforgeConnection = None

class TinkerforgeConnection(object):

	ipcon = None
	current_entries = dict()

	def cb_enumerate(self, uid, connected_uid, position, hardware_version, firmware_version, device_identifier, enumeration_type):
	
		if enumeration_type == IPConnection.ENUMERATION_TYPE_DISCONNECTED:
			del self.current_entries[uid]
			
		else:
			if device_identifier == 13:
				self.current_entries.update({uid: "Master Brick"})
			elif device_identifier == 21:
				self.current_entries.update({uid: "Ambient Light Bricklet"})
			elif device_identifier == 229:
				self.current_entries.update({uid: "Distance US Bricklet"})
			elif device_identifier == 235:
				self.current_entries.update({uid: "RemoteSwitchBricklet"})
			else:
				self.current_entries.update({uid: "device_identifier = "+device_identifier})

	def switchSocket(self, uid, address, unit, state):
		rs = BrickletRemoteSwitch(uid, self.ipcon)
		rs.switch_socket_b(address, unit, state)

	def __init__(self):
		self.ipcon = IPConnection()
		self.ipcon.connect('localhost', 4223)
		self.ipcon.register_callback(IPConnection.CALLBACK_ENUMERATE, self.cb_enumerate)
		self.ipcon.enumerate()

class Webserver(object):

	# Entry

	@cherrypy.expose
	def index(self):
		return "Hello world!"

	# Buttons

	@cherrypy.expose
	def button_nXN_29_1_on(self):
		tinkerforgeConnection.switchSocket("nXN", 29, 1, 1)
		return "Aktiviere 29_1"
		
	@cherrypy.expose
	def button_nXN_29_1_off(self):
		tinkerforgeConnection.switchSocket("nXN", 29, 1, 0)
		return "Deaktiviere 29_1"

	@cherrypy.expose
	def button_nXN_30_1_on(self):
		tinkerforgeConnection.switchSocket("nXN", 30, 1, 1)
		return "Aktiviere 30_1"
		
	@cherrypy.expose
	def button_nXN_30_1_off(self):
		tinkerforgeConnection.switchSocket("nXN", 30, 1, 0)
		return "Deaktiviere 30_1"
		
	@cherrypy.expose
	def button_nXN_30_2_on(self):
		tinkerforgeConnection.switchSocket("nXN", 30, 2, 1)
		return "Aktiviere 30_2"
		
	@cherrypy.expose
	def button_nXN_30_2_off(self):
		tinkerforgeConnection.switchSocket("nXN", 30, 2, 0)
		return "Deaktiviere 30_2"
		
	@cherrypy.expose
	def button_nXN_30_3_on(self):
		tinkerforgeConnection.switchSocket("nXN", 30, 3, 1)
		return "Aktiviere 30_3"
		
	@cherrypy.expose
	def button_nXN_30_3_off(self):
		tinkerforgeConnection.switchSocket("nXN", 30, 3, 0)
		return "Deaktiviere 30_3"
		
	@cherrypy.expose
	def button_nXN_31_1_on(self):
		tinkerforgeConnection.switchSocket("nXN", 31, 1, 1)
		return "Aktiviere 31_1"
		
	@cherrypy.expose
	def button_nXN_31_1_off(self):
		tinkerforgeConnection.switchSocket("nXN", 31, 1, 0)
		return "Deaktiviere 31_1"
		
	@cherrypy.expose
	def button_nXN_31_2_on(self):
		tinkerforgeConnection.switchSocket("nXN", 31, 2, 1)
		return "Aktiviere 31_2"
		
	@cherrypy.expose
	def button_nXN_31_2_off(self):
		tinkerforgeConnection.switchSocket("nXN", 31, 2, 0)
		return "Deaktiviere 31_2"
		
	# Informationen
	
	@cherrypy.expose
	def connectedDevices(self):
		if len(tinkerforgeConnection.current_entries) == 0:
			return "<li>Keine Geräte angeschlossen</li>"
		string = ""
		for key in tinkerforgeConnection.current_entries:
			string += "<li>"+key+" ("+tinkerforgeConnection.current_entries[key]+")</li>"
		return string

if __name__ == '__main__':
	conf = {
		'global': {
			'server.socket_port': 8081
		},
		'/': {
			'tools.staticdir.root': os.path.abspath(os.getcwd())
		},
		'/static': {
			'tools.staticdir.on': True,
			'tools.staticdir.dir': './static',
			'tools.staticdir.index': 'index.html'
		}
	}
	tinkerforgeConnection = TinkerforgeConnection()
	cherrypy.quickstart(Webserver(), '/', conf)