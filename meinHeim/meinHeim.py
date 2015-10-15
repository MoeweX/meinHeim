#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import string
import time
import datetime
from threading import Thread

import cherrypy

from modules import TinkerforgeConnection
from modules import BVG

##########################################################################################
#Global Variables
##########################################################################################
tinkerforgeConnection = None
bvg = None
rules = None

##########################################################################################
#Collection of all Rules
##########################################################################################
class Rules(object):

	# Automatic Watering
		
	watering_rule_keep_alive = True
	watering_rule_thread = None
	
	def watering_rule(self):
		while self.watering_rule_keep_alive:
			now = datetime.datetime.now()
			if now.hour == 9 or now.hour == 19:
				cherrypy.log("It is " + str(now.hour) + ":" + str(now.minute) + ", started watering.")
				tinkerforgeConnection.switch_socket("nXN", 31, 1, 1)
				time.sleep(60)
				cherrypy.log("It is " + str(now.hour) + ":" + str(now.minute) + ", stoped watering.")
				tinkerforgeConnection.switch_socket("nXN", 31, 1, 0)
				
			time.sleep(50)
		cherrypy.log("Stopped Watering Rule")
	
	# Turn on Desk Lamp when Sitting at Table
	
	desk_lamb_rule_keep_alive = True
	desk_lamb_rule_thread = None
		
	def desk_lamb_rule(self):
		send_on = False
		while self.desk_lamb_rule_keep_alive:
			if tinkerforgeConnection.get_distance("iTm") <= 1500 and tinkerforgeConnection.get_illuminance("amm") <= 30 and send_on == False:
				tinkerforgeConnection.switch_socket("nXN", 30, 3, 1)
				send_on = True
			elif (tinkerforgeConnection.get_distance("iTm") > 1500 or tinkerforgeConnection.get_illuminance("amm") > 30) and send_on == True:
				tinkerforgeConnection.switch_socket("nXN", 30, 3, 0)
				send_on = False		
			time.sleep(10)
		cherrypy.log("Stopped Desk Lamb Rule")
	
	# TODO Generalize start_rule method	
	def start_watering_rule(self):
		if self.watering_rule_thread == None: # check whether not initialized
			cherrypy.log("Started Watering Rule")
			self.watering_rule_thread = Thread(name="Watering Rule", target=self.watering_rule)
			self.watering_rule_thread.setDaemon(True)
			self.watering_rule_keep_alive = True
			self.watering_rule_thread.start()
		elif self.watering_rule_thread.isAlive(): # check whether still alive
			cherrypy.log("Watering Rule was still Alive")
			self.watering_rule_keep_alive = True
		else: # initialized but dead
			cherrypy.log("Started Watering Rule")
			self.watering_rule_thread = Thread(name="Watering Rule", target=self.watering_rule)
			self.watering_rule_thread.setDaemon(True)
			self.watering_rule_keep_alive = True
			self.watering_rule_thread.start()
			
	def start_desk_lamb_rule(self):
		if self.desk_lamb_rule_thread == None: # check whether not initialized
			cherrypy.log("Started Desk Lamp Rule")
			self.desk_lamb_rule_thread = Thread(name="Desk Lamp Rule", target=self.desk_lamb_rule)
			self.desk_lamb_rule_thread.setDaemon(True)
			self.desk_lamb_rule_keep_alive = True
			self.desk_lamb_rule_thread.start()
		elif self.desk_lamb_rule_thread.isAlive(): # check whether still alive
			cherrypy.log("Desk Lamp was still Alive")
			self.desk_lamb_rule_keep_alive = True
		else: # initialized but dead
			cherrypy.log("Started Desk Lamp Rule")
			self.desk_lamb_rule_thread = Thread(name="Desk Lamp Rule", target=self.desk_lamb_rule)
			self.desk_lamb_rule_thread.setDaemon(True)
			self.desk_lamb_rule_keep_alive = True
			self.desk_lamb_rule_thread.start()
			
			
	def __init__(self):
		self.start_watering_rule()
		self.start_desk_lamb_rule()

##########################################################################################
#The Webserver
##########################################################################################
class Webserver(object):

	# Entrypoint

	@cherrypy.expose
	def index(self):
		raise cherrypy.HTTPRedirect("/static")

	# Buttons switch_socket

	@cherrypy.expose
	def button_nXN_29_1_on(self):
		tinkerforgeConnection.switch_socket("nXN", 29, 1, 1)
		return "Aktiviere 29_1"
		
	@cherrypy.expose
	def button_nXN_29_1_off(self):
		tinkerforgeConnection.switch_socket("nXN", 29, 1, 0)
		return "Deaktiviere 29_1"

	@cherrypy.expose
	def button_nXN_30_1_on(self):
		tinkerforgeConnection.switch_socket("nXN", 30, 1, 1)
		return "Aktiviere 30_1"
		
	@cherrypy.expose
	def button_nXN_30_1_off(self):
		tinkerforgeConnection.switch_socket("nXN", 30, 1, 0)
		return "Deaktiviere 30_1"
		
	@cherrypy.expose
	def button_nXN_30_2_on(self):
		tinkerforgeConnection.switch_socket("nXN", 30, 2, 1)
		return "Aktiviere 30_2"
		
	@cherrypy.expose
	def button_nXN_30_2_off(self):
		tinkerforgeConnection.switch_socket("nXN", 30, 2, 0)
		return "Deaktiviere 30_2"
		
	@cherrypy.expose
	def button_nXN_30_3_on(self):
		tinkerforgeConnection.switch_socket("nXN", 30, 3, 1)
		return "Aktiviere 30_3"
		
	@cherrypy.expose
	def button_nXN_30_3_off(self):
		tinkerforgeConnection.switch_socket("nXN", 30, 3, 0)
		return "Deaktiviere 30_3"
		
	@cherrypy.expose
	def button_nXN_31_1_on(self):
		tinkerforgeConnection.switch_socket("nXN", 31, 1, 1)
		return "Aktiviere 31_1"
		
	@cherrypy.expose
	def button_nXN_31_1_off(self):
		tinkerforgeConnection.switch_socket("nXN", 31, 1, 0)
		return "Deaktiviere 31_1"
		
	@cherrypy.expose
	def button_nXN_31_2_on(self):
		tinkerforgeConnection.switch_socket("nXN", 31, 2, 1)
		return "Aktiviere 31_2"
		
	@cherrypy.expose
	def button_nXN_31_2_off(self):
		tinkerforgeConnection.switch_socket("nXN", 31, 2, 0)
		return "Deaktiviere 31_2"
	
	# Rules
	
	@cherrypy.expose
	def watering_rule_on(self):
		rules.start_watering_rule()
		return "Watering Rule activated"
	
	@cherrypy.expose
	def watering_rule_off(self):
		rules.watering_rule_keep_alive = False
		return "Watering Rule deactivated"
	
	@cherrypy.expose
	def watering_rule_status(self):
		if rules.watering_rule_keep_alive:
			return "<a href='.' onclick='return $.ajax(\"../watering_rule_off\");'>Aktiv</a>"
		else:
			return "<a href='.' onclick='return $.ajax(\"../watering_rule_on\");'>Deaktiv</a>"
	
	@cherrypy.expose
	def desk_lamb_rule_on(self):
		rules.start_desk_lamb_rule()
		return "Desk Lamb Rule activated"
	
	@cherrypy.expose
	def desk_lamb_rule_off(self):
		rules.desk_lamb_rule_keep_alive = False
		return "Desk Lamb Rule deactivated"
	
	@cherrypy.expose
	def desk_lamb_rule_status(self):
		if rules.desk_lamb_rule_keep_alive:
			return "<a href='.' onclick='return $.ajax(\"../desk_lamb_rule_off\");'>Aktiv</a>"
		else:
			return "<a href='.' onclick='return $.ajax(\"../desk_lamb_rule_on\");'>Deaktiv</a>"	
		
	# Additional Informationen
	
	@cherrypy.expose
	def information_connected_devices(self):
		if len(tinkerforgeConnection.current_entries) == 0:
			return "<li>Keine Geräte angeschlossen</li>"
		string = ""
		for key in tinkerforgeConnection.current_entries:
			string += "<li>"+key+" ("+tinkerforgeConnection.current_entries[key]+")</li>"
		return string
	
	@cherrypy.expose
	def information_amm_illuminance(self):
		return str(tinkerforgeConnection.get_illuminance("amm"))
		
	@cherrypy.expose
	def information_iTm_distance(self):
		return str(tinkerforgeConnection.get_distance("iTm"))
		
	@cherrypy.expose
	def information_bvg(self):
		array = bvg.call()
		if array == None:
			return "<li>Keine Abfahrtzeiten verfügbar</li>"
		string = ""
		for entry in array:
			string += "<li>"+entry[3] + " -> " + entry[1]+ " (" + entry[2] + ")</li>"
		return string

if __name__ == '__main__':
	conf = {
		'global': {
			'server.socket_port': 8081,
			'server.socket_host': '0.0.0.0',
			'log.error_file': 'error.log'
		},
		'/': {
			'tools.staticdir.root': os.path.abspath(os.getcwd())
		},
		'/static': {
			'tools.staticdir.on': True,
			'tools.staticdir.dir': './website',
			'tools.staticdir.index': 'index.html'
		}
	}
	tinkerforgeConnection = TinkerforgeConnection()
	bvg = BVG("Seesener Str. (Berlin)", limit=4)
	rules = Rules()
	cherrypy.quickstart(Webserver(), '/', conf)