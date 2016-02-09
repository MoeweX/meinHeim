#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import string
import time
import datetime
from threading import Thread
import abc

import cherrypy

from modules import TinkerforgeConnection
from modules import BVG

##########################################################################################
#Global Variables
##########################################################################################
tinkerforge_connection = None
bvg = None
rules = None

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
					cherrypy.log(self.tname + " was still alive!")
					return

			# not initialized or dead, does not matter
			cherrypy.log("Activated Rule " + self.tname + ".")
			self.thread = Thread(name=self.tname, target=self.rule)
			self.thread.setDaemon(True)
			self.thread.start()

		def deactivate_rule(self):
			cherrypy.log("Rule " + self.tname + "will not be kept alive.")
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
					cherrypy.log("It is " + str(now.hour) + ":" + str(now.minute) + ", started watering.")
					#tinkerforge_connection.switch_socket("nXN", 31, 1, 1)
					time.sleep(60)
					cherrypy.log("It is " + str(now.hour) + ":" + str(now.minute) + ", stopped watering.")
					#tinkerforge_connection.switch_socket("nXN", 31, 1, 0)
				time.sleep(50)
			cherrypy.log(self.tname + " was no longer kept alive.")

	class Balkon_Rule(Generale_Rule):
		def rule(self):
			while self.keep_alive:
				now = datetime.datetime.now()
				if (now.hour == 17 and now.minute == 0):
					cherrypy.log("It is " + str(now.hour) + ":" + str(now.minute) + ", activated Balkonbeleuchtung.")
					tinkerforgeConnection.switch_socket("nXN", 50, 1, 1)
				if (now.hour == 22 and now.minute == 0):
					cherrypy.log("It is " + str(now.hour) + ":" + str(now.minute) + ", deactivated Balkonbeleuchtung.")
					tinkerforgeConnection.switch_socket("nXN", 50, 1, 0)
				time.sleep(50)
			cherrypy.log(self.tname + " was no longer kept alive.")

	class Desklamp_Rule(Generale_Rule):
		def rule(self):
			send_on = False
			while self.keep_alive:
				if tinkerforge_connection.get_distance("iTm") <= 1500 and tinkerforge_connection.get_illuminance("amm") <= 30 and send_on == False:
					tinkerforge_connection.switch_socket("nXN", 30, 3, 1)
					send_on = True
				elif (tinkerforge_connection.get_distance("iTm") > 1500 or tinkerforge_connection.get_illuminance("amm") > 30) and send_on == True:
					tinkerforge_connection.switch_socket("nXN", 30, 3, 0)
					send_on = False
				time.sleep(10)
			cherrypy.log(self.tname + " was no longer kept alive.")


	# define public variables for all rules
	watering_rule = None
	balkon_rule = None
	desklamp_rule = None

	def __init__(self):
		self.watering_rule = Rules.Watering_Rule("Watering Rule")
		self.balkon_rule = Rules.Balkon_Rule("Balkon Rule")
		self.desklamp_rule = Rules.Desklamp_Rule("Desklamp Rule")

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
			return "Tried to switch socket"

		def create_socket_entry(self, name, address, unit):
			return (
			"<div class='large-12 columns'>" +
				"<div class='panel clearfix'>" +
					"<p>" + name + " (" + str(address) + "_" + str(unit) + ", nXN)</p>" +
					"<button class='small success right button' "+
					"onclick='console.log($.ajax(\"/socket/nXN?address=" + str(address) +
					"&unit=" + str(unit) +
					"&state=1\"));' style='width:100px'>An</button>" +
					"<button class='small alert right button' "+
					"onclick='console.log($.ajax(\"/socket/nXN?address=" + str(address) +
					"&unit=" + str(unit) +
					"&state=0\"));' style='width:100px'>Aus</button>"
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
		def watering_rule_on(self):
			rules.watering_rule.activate_rule()
			return "Watering Rule activated"

		@cherrypy.expose
		def watering_rule_off(self):
			rules.watering_rule.keep_alive = False
			return "Test Rule deactivated"

		@cherrypy.expose
		def watering_rule_status(self):
			if rules.watering_rule.keep_alive:
				return "<a href='.' onclick='return $.ajax(\"/rule/watering_rule_off\");'>Aktiv</a>"
			else:
				return "<a href='.' onclick='return $.ajax(\"/rule/watering_rule_on\");'>Deaktiv</a>"

		@cherrypy.expose
		def balkon_rule_on(self):
			rules.balkon_rule.activate_rule()
			return "Balkon Rule activated"

		@cherrypy.expose
		def balkon_rule_off(self):
			rules.balkon_rule.keep_alive = False
			return "Balkon Rule deactivated"

		@cherrypy.expose
		def balkon_rule_status(self):
			if rules.balkon_rule.keep_alive:
				return "<a href='.' onclick='return $.ajax(\"/rule/balkon_rule_off\");'>Aktiv</a>"
			else:
				return "<a href='.' onclick='return $.ajax(\"/rule/balkon_rule_on\");'>Deaktiv</a>"

		@cherrypy.expose
		def desk_lamb_rule_on(self):
			rules.desklamp_rule.activate_rule()
			return "Desk Lamb Rule activated"

		@cherrypy.expose
		def desk_lamb_rule_off(self):
			rules.desklamp_rule.keep_alive = False
			return "Desk Lamb Rule deactivated"

		@cherrypy.expose
		def desk_lamb_rule_status(self):
			if rules.desklamp_rule.keep_alive:
				return "<a href='.' onclick='return $.ajax(\"/rule/desk_lamb_rule_off\");'>Aktiv</a>"
			else:
				return "<a href='.' onclick='return $.ajax(\"/rule/desk_lamb_rule_on\");'>Deaktiv</a>"

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
			return str(tinkerforge_connection.get_illuminance("amm"))

		@cherrypy.expose
		def iTm_distance(self):
			return str(tinkerforge_connection.get_distance("iTm"))

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
			'log.error_file': 'error.log',
			'log.access_file': 'access.log'
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

	# start all needed modules
	tinkerforge_connection = TinkerforgeConnection()
	bvg = BVG("Seesener Str. (Berlin)", limit=4)

	# load the rules
	rules = Rules()

	# start the webserver
	cherrypy.tree.mount(Webserver().socket, '/socket')
	cherrypy.tree.mount(Webserver().dimmer, '/dimmer')
	cherrypy.tree.mount(Webserver().rule, '/rule')
	cherrypy.tree.mount(Webserver().additional_information, '/additional_information')
	cherrypy.quickstart(Webserver(), '/', conf)
