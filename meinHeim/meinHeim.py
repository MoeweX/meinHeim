#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import string
import time
import datetime
from threading import Thread
import abc
import logging
import logging.config

import cherrypy

from modules import TinkerforgeConnection
from modules import BVG

##########################################################################################
#Global Variables
##########################################################################################
tinkerforge_connection = None
bvg = None
rules = None
log = logging.getLogger() # the logger

##########################################################################################
#Collection of all Rules
##########################################################################################
class Rules(object):

	class Generale_Rule():
		__metaclass__ = abc.ABCMeta

		keep_alive = False
		thread = None
		tname = ""

		def activate_rule(self):
			self.keep_alive = True
			if self.thread != None: # check whether not initialized
				if self.thread.isAlive(): # check whether was still alive
					log.info(self.tname + " was still alive!")
					return

			# not initialized or dead, does not matter
			log.info("Activated Rule " + self.tname + ".")
			self.thread = Thread(name=self.tname, target=self.rule)
			self.thread.setDaemon(True)
			self.thread.start()

		def deactivate_rule(self):
			log.info("Rule " + self.tname + " will not be kept alive.")
			self.keep_alive = False

		@abc.abstractmethod
		def rule(self):
			"This method is abstract"

		def __init__(self, tname):
			self.tname = tname

	class Watering_Rule(Generale_Rule):
		def rule(self):
			while self.keep_alive:
				now = datetime.datetime.now()
				if (now.hour == 9 and now.minute == 0) or (now.hour == 19 and now.minute == 0):
					log.info("It is " + str(now.hour) + ":" + str(now.minute) + ", started watering.")
					tinkerforge_connection.switch_socket("nXN", 50, 1, 1)
					time.sleep(60)
					log.info("It is " + str(now.hour) + ":" + str(now.minute) + ", stopped watering.")
					tinkerforge_connection.switch_socket("nXN", 50, 1, 0)
				time.sleep(50)
			log.info(self.tname + " was no longer kept alive.")

	class Balkon_Rule(Generale_Rule):
		def rule(self):
			while self.keep_alive:
				now = datetime.datetime.now()
				if (now.hour == 17 and now.minute == 0):
					log.info("It is " + str(now.hour) + ":" + str(now.minute) + ", activated Balkonbeleuchtung.")
					tinkerforge_connection.switch_socket("nXN", 50, 1, 1)
				if (now.hour == 22 and now.minute == 0):
					log.info("It is " + str(now.hour) + ":" + str(now.minute) + ", deactivated Balkonbeleuchtung.")
					tinkerforge_connection.switch_socket("nXN", 50, 1, 0)
				time.sleep(50)
			log.info(self.tname + " was no longer kept alive.")

	# define public variables for all rules
	active_rules = None

	def __init__(self):
		# specify which rules should be currently active
		self.active_rules = [
			#Rules.Watering_Rule("Bewässerungsregel (9 + 19)"),
			Rules.Balkon_Rule("Balkonregel (17 - 22)"),
		]

##########################################################################################
#The Webserver
##########################################################################################
class Webserver(object):

	# initialize subclasses
	def __init__(self):
		self.socket = self.Socket()
		self.dimmer = self.Dimmer()
		self.rule = self.Rule()
		self.additional_information = self.AdditionalInformation()

	# entrypoint to webpage
	@cherrypy.expose
	def index(self):
			raise cherrypy.HTTPRedirect("/static")

	# buttons to switch normal sockets + shutdown dimmer
	class Socket():

		@cherrypy.expose
		def list(self):
			list = self.create_socket_entry("Schreibtischlampe", 30, 3)
			list += self.create_socket_entry("Hintergrundbeleuchtung", 30, 2)
			list += self.create_socket_entry("Laterne", 31, 2)
			#list += self.create_socket_entry("Nachtlicht", 25, 1)
			list += self.create_socket_entry("Balkonbeleuchtung", 50, 1)
			return list

		@cherrypy.expose
		def nXN(self, address=-1, unit=-1, state=-1):
			if (address == -1 or unit == -1 or state == -1):
				return ("Invalid information: " + str(address)
					+ ", " + str(unit) + ", " + str(state))
			tinkerforge_connection.switch_socket(
				"nXN",
				int(address),
				int(unit),
				int(state))
			log.info("Tried to  switch socket " + str(address) + "-" + str(unit))

		def create_socket_entry(self, name, address, unit):
			return (
			"<div class='large-12 columns'>" +
				"<div class='panel clearfix'>" +
					"<p>" + name + " (" + str(address) + "_" + str(unit) + ", nXN)</p>" +
					"<button class='small success right button' "+
					"onclick='$.ajax(\"/socket/nXN?address=" + str(address) +
						"&unit=" + str(unit) +
						"&state=1\");' style='width:100px'>An</button>" +
					"<button class='small alert right button' "+
					"onclick='$.ajax(\"/socket/nXN?address=" + str(address) +
						"&unit=" + str(unit) +
						"&state=0\");' style='width:100px'>Aus</button>"
				"</div>" +
			"</div>"
			)

	# buttons that control dimmer
	class Dimmer():
		# TODO does not work yet
		value_25_1 = 10

		@cherrypy.expose
		def button_nXN_25_1_increase(self):
			if self.value_25_1 < 15:
				self.value_25_1 = self.value_25_1 + 1
				tinkerforge_connection.dimm_socket("nXN", 25, 1, self.value_25_1)
				return "Neuer Dimmwert 25_1 = " + str(self.value_25_1)
			return "Dimmwert war schon bei 15"

		@cherrypy.expose
		def button_nXN_25_1_decrease(self):
			if self.value_25_1 > 0:
				self.value_25_1 = self.value_25_1 - 1
				tinkerforge_connection.dimm_socket("nXN", 25, 1, self.value_25_1)
				return "Neuer Dimmwert 25_1 = " + str(self.value_25_1)
			return "Dimmwert war schon bei 0"

		@cherrypy.expose
		def button_nXN_25_1_off(self):
			tinkerforge_connection.switch_socket("nXN", 25, 1, 0)
			return "Deaktiviere 25_0"

	# buttons that control the rules
	class Rule():

		@cherrypy.expose
		def list(self):
			list = ""
			for index in range(0, len(rules.active_rules)):
				list += self.create_rule_entry(index)
			return list

		@cherrypy.expose
		def toggle_rule_keep_alive(self, position, keep_alive):
			position = int(position)
			if position >= 0 and position < len(rules.active_rules):
				name = name = rules.active_rules[position].tname
				if keep_alive == "false":
					rules.active_rules[position].deactivate_rule()
				else:
					rules.active_rules[position].activate_rule()
			else:
				log.warn("No rule at position " + str(position))

		def create_rule_entry(self, position):
			name = rules.active_rules[position].tname
			if rules.active_rules[position].keep_alive:
				checked = "checked "
			else:
				checked = ""
			return (
			"<tr><td>" + name + "</td>" +
				"<td><div class='switch small' style='margin-bottom:0rem'>" +
					 "<input id= '" + name + "' type='checkbox' " + checked +
					 	"onclick='$.ajax(\"/rule/toggle_rule_keep_alive?" +
						"position=" + str(position) +
						"&keep_alive=\" + event.target.checked);'>" +
					 "<label for='" + name + "'></label>" +
				"</div></td>" +
			"</td>"
			)


	# queries that provide additional informationen
	class AdditionalInformation():
		@cherrypy.expose
		def connected_devices(self):
			if len(tinkerforge_connection.current_entries) == 0:
				return "<li>Keine Geräte angeschlossen</li>"
			string = ""
			for key in tinkerforge_connection.current_entries:
				string += "<li>"+key+" ("+tinkerforge_connection.current_entries[key]+")</li>"
			return string

		@cherrypy.expose
		def amm_illuminance(self):
			return (
			"<li id='information_amm_illuminance'>Aktuelle Helligkeit (amm): " +
			str(tinkerforge_connection.get_illuminance("amm")) + " Lux</li>"
			)

		@cherrypy.expose
		def bvg(self):
			array = bvg.call()
			if array == None:
				return "<li>Keine Abfahrtzeiten verfügbar</li>"
			string = ""
			for entry in array:
				string += "<li>"+entry[3] + " -> " + entry[1]+ " (" + entry[2] + ")</li>"
			return string

##########################################################################################
#The Entrypoint of the Application
##########################################################################################
if __name__ == '__main__':
	# the configuration for the webserver
	conf = {
		'global': {
			'server.socket_port': 8081,
			'server.socket_host': '0.0.0.0',
			'log.error_file': '',
			'log.access_file': '',
			'log.screen': False
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

	#the logging configuratoin
	log_conf = {
	    'version': 1,

	    'formatters': {
	        'void': {
	            'format': ''
	        },
	        'standard': {
	            'format': '%(asctime)s [%(levelname)s] %(message)s'
	        },
	    },
	    'handlers': {
	        'default': {
	            'level':'INFO',
	            'class':'logging.StreamHandler',
	            'formatter': 'standard',
	            'stream': 'ext://sys.stdout'
	        },
	        'default_file': {
	            'level':'INFO',
	            'class':'logging.handlers.RotatingFileHandler',
	            'formatter': 'standard',
	            'filename': 'default.log',
	            'maxBytes': 10485760,
	            'backupCount': 20,
	            'encoding': 'utf8'
	        },
	        'cherrypy_default_error': {
	            'level':'INFO',
	            'class':'logging.StreamHandler',
	            'formatter': 'standard',
	            'stream': 'ext://sys.stdout'
	        },
	        'cherrypy_default_error_file': {
	            'level':'INFO',
	            'class':'logging.handlers.RotatingFileHandler',
	            'formatter': 'standard',
	            'filename': 'cherrypy_default_error.log',
	            'maxBytes': 10485760,
	            'backupCount': 20,
	            'encoding': 'utf8'
	        },
	        'cherrypy_access': {
	            'level':'INFO',
	            'class': 'logging.handlers.RotatingFileHandler',
	            'formatter': 'void',
	            'filename': 'cherrypy_access.log',
	            'maxBytes': 10485760,
	            'backupCount': 20,
	            'encoding': 'utf8'
	        }
	    },
	    'loggers': {
	        '': {
	            'handlers': ['default', 'default_file'],
	            'level': 'INFO'
	        },
	        'cherrypy.access': {
	            'handlers': ['cherrypy_access'],
	            'level': 'INFO',
	            'propagate': False
	        },
	        'cherrypy.error': {
	            'handlers': ['cherrypy_default_error', 'cherrypy_default_error_file'],
	            'level': 'INFO',
	            'propagate': False
	        },
	    }
	}

	# start all needed modules
	tinkerforge_connection = TinkerforgeConnection()
	bvg = BVG("Seesener Str. (Berlin)", limit=4)

	# load the rules
	rules = Rules()

	# start the webserver and configure logging
	cherrypy.engine.unsubscribe('graceful', cherrypy.log.reopen_files)
	logging.config.dictConfig(log_conf)
	cherrypy.tree.mount(Webserver().socket, '/socket')
	cherrypy.tree.mount(Webserver().dimmer, '/dimmer')
	cherrypy.tree.mount(Webserver().rule, '/rule')
	cherrypy.tree.mount(Webserver().additional_information, '/additional_information')
	cherrypy.quickstart(Webserver(), '/', conf)
