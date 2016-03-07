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
# Global Variables
##########################################################################################
tinkerforge_connection = None
bvg = None
rules = None
log = logging.getLogger()  # the logger


##########################################################################################
# Collection of all Rules
##########################################################################################


class Rules(object):

    class Generale_Rule():
        __metaclass__ = abc.ABCMeta

        keep_alive = False
        thread = None
        tname = ""

        def activate_rule(self):
            self.keep_alive = True
            if self.thread is not None:  # check whether already initialized
                if self.thread.isAlive():  # check whether was still alive
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
                if ((now.hour == 9 and now.minute == 0) or
                        (now.hour == 19 and now.minute == 0)):
                    log.info("It is {0!s}:{1!s}, started watering."
                             .format(now.hour, now.minute))
                    tinkerforge_connection.switch_socket("nXN", 50, 1, 1)
                    time.sleep(60)
                    log.info("It is {0!s}:{1!s}, stopped watering."
                             .format(now.hour, now.minute))
                    tinkerforge_connection.switch_socket("nXN", 50, 1, 0)
                time.sleep(50)
            log.info(self.tname + " was no longer kept alive.")

    class Balkon_Rule(Generale_Rule):
        def rule(self):
            while self.keep_alive:
                now = datetime.datetime.now()
                if (now.hour == 17 and now.minute == 0):
                    log.info("It is {0!s}:{1!s}, activated Balkonbeleuchtung."
                             .format(now.hour, now.minute))
                    tinkerforge_connection.switch_socket("nXN", 50, 1, 1)
                if (now.hour == 22 and now.minute == 0):
                    log.info("It is {0!s}:{1!s}, deactivated Balkonbeleuchtung."
                             .format(now.hour, now.minute))
                    tinkerforge_connection.switch_socket("nXN", 50, 1, 0)
                time.sleep(50)
            log.info(self.tname + " was no longer kept alive.")

    # define public variables for all rules
    active_rules = None

    def __init__(self):
        # specify which rules should be currently active
        self.active_rules = [
            # Rules.Watering_Rule("Bewässerungsregel (9 + 19)"),
            Rules.Balkon_Rule("Balkonregel (17 - 22)"),
        ]


##########################################################################################
# The Webserver
##########################################################################################


class Webserver(object):

    # initialize subclasses
    def __init__(self):
        self.socket = self.Socket()
        self.rule = self.Rule()
        self.additional_information = self.AdditionalInformation()

    # entrypoint to webpage
    @cherrypy.expose
    def index(self):
            raise cherrypy.HTTPRedirect("/static")

    # control sockets and dimmer
    class Socket():

        @cherrypy.expose
        def list(self):
            list = self.create_socket_entry("Schreibtischlampe", 30, 3)
            list += self.create_socket_entry("Hintergrundbeleuchtung", 30, 2)
            list += self.create_socket_entry("Laterne", 31, 2)
            list += self.create_dim_entry("Nachtlicht", 25, 1)
            list += self.create_socket_entry("Balkonbeleuchtung", 50, 1)
            return list

        @cherrypy.expose
        def switch(self, address=-1, unit=-1, state=-1):
            if (address == -1 or unit == -1 or state == -1):
                return ("Invalid information: {0!s}, {1!s}, {2!s}."
                        .format(address, unit, state))
            tinkerforge_connection.switch_socket("nXN", int(address), int(unit),
                                                 int(state))
            log.info("Sending signal to switch socket {0!s}-{1!s} to {2!s}."
                     .format(address, unit, state))

        @cherrypy.expose
        def dim(self, address=-1, unit=-1, dimValue=-1):
            if (address == -1 or unit == -1 or dimValue == -1):
                return ("Invalid information: {0!s}, {1!s}, {2!s}."
                        .format(address, unit, dimValue))
            tinkerforge_connection.dim_socket("nXN", int(address), int(unit),
                                              int(dimValue))
            log.info("Tried to dim socket {0!s}-{1!s} to {2!s}."
                     .format(address, unit, dimValue))

        def create_socket_entry(self, name, address, unit):
            return """
                <div class='large-12 columns'>
                    <div class='callout secondary'>
                        <p>{n} ({a}_{u}, nXN)</p>
                        <div class='expanded button-group'>
                            <button class='alert button' onclick='$.ajax(
                                "/socket/switch?address={a}&unit={u}&state=0");'>Aus
                            </button>
                            <button class='success button' onclick='$.ajax(
                                "/socket/switch?address={a}&unit={u}&state=1");'>An
                            </button>
                        </div>
                    </div>
                </div>
            """.format(n=name, a=str(address), u=str(unit))

        def create_dim_entry(self, name, address, unit):
            id = str(address) + "_" + str(unit)
            return """
            <div class='large-12 columns'>
                <div class='callout secondary'>
                    <p>{n} ({a}_{u}, nXN)</p>
                    <div class='slider' data-slider data-initial-start='0' data-end='15'>
                        <span class='slider-handle' data-slider-handle role='slider'
                          tabindex='1' onclick='$.ajax(
                          "/socket/dim?address={a}&unit={u}&dimValue="
                          + $("#{i}").val());'>
                        </span>
                        <span class='slider-fill' data-slider-fill></span>
                        <input id='{i}' type='hidden'></div>
                        <button class='alert expanded button' onclick='$.ajax(
                          "/socket/switch?address={a}&unit={u}&state=0");'>Aus
                        </button>
                    </div>
                </div>
            """.format(n=name, a=str(address), u=str(unit), i=id)

    # control rules
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
            return """
            <tr>
                <td>{n}</td>
                <td>
                    <div class='switch'>
                        <input class='switch-input' id='{n}' type='checkbox' {c} onclick=
                          '$.ajax("/rule/toggle_rule_keep_alive?position={p}&keep_alive="
                          + event.target.checked);'>
                        <label class='switch-paddle' for='{n}'></label>
                    </div>
                </td>
            </tr>
            """.format(n=name, p=str(position), c=checked)

    # provides additional informationen
    class AdditionalInformation():
        @cherrypy.expose
        def connected_devices(self):
            if len(tinkerforge_connection.current_entries) == 0:
                return "<li>Keine Geräte angeschlossen</li>"
            string = ""
            for key in tinkerforge_connection.current_entries:
                string += ("<li>{0} ({1})</li>"
                           .format(key, tinkerforge_connection.current_entries[key]))
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
            if array is None:
                return "<li>Keine Abfahrtzeiten verfügbar</li>"
            string = ""
            for entry in array:
                string += "<li>{0} -> {1} ({2})</li>".format(entry[3], entry[1], entry[2])
            return string


##########################################################################################
# The Entrypoint of the Application
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

    # the logging configuratoin
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
                'level': 'INFO',
                'class': 'logging.StreamHandler',
                'formatter': 'standard',
                'stream': 'ext://sys.stdout'
            },
            'default_file': {
                'level': 'INFO',
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'standard',
                'filename': 'default.log',
                'maxBytes': 10485760,
                'backupCount': 20,
                'encoding': 'utf8'
            },
            'cherrypy_default_error': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
                'formatter': 'standard',
                'stream': 'ext://sys.stdout'
            },
            'cherrypy_default_error_file': {
                'level': 'INFO',
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'standard',
                'filename': 'cherrypy_default_error.log',
                'maxBytes': 10485760,
                'backupCount': 20,
                'encoding': 'utf8'
            },
            'cherrypy_access': {
                'level': 'INFO',
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
    cherrypy.tree.mount(Webserver().rule, '/rule')
    cherrypy.tree.mount(Webserver().additional_information, '/additional_information')
    cherrypy.quickstart(Webserver(), '/', conf)
