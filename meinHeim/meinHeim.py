#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import datetime
import logging.config

import cherrypy
from config import log_conf, conf

from modules import Rule
from modules import TinkerforgeConnection
from modules import BVG


log = logging.getLogger()  # the logger

##########################################################################################
# Data class to store global information
##########################################################################################


class Data(object):
    bvg = None
    active_rules = []
    tinkerforge_connection = None
    wakeup_time = "0:0"


##########################################################################################
# Rule logic
##########################################################################################

def watering_rule():
    now = datetime.datetime.now()
    if (now.hour == 9 and now.minute == 0) or (now.hour == 19 and now.minute == 0):
        log.info("It is {0!s}:{1!s}, started watering.".format(now.hour, now.minute))
        Data.tinkerforge_connection.switch_socket("nXN", 50, 1, 1)
        time.sleep(60)
        log.info("It is {0!s}:{1!s}, stopped watering.".format(now.hour, now.minute))
        Data.tinkerforge_connection.switch_socket("nXN", 50, 1, 0)


def balkony_rule():
    now = datetime.datetime.now()
    if now.hour == 17 and now.minute == 0:
        log.info("It is {0!s}:{1!s}, activated Balkonbeleuchtung.".format(now.hour, now.minute))
        Data.tinkerforge_connection.switch_socket("nXN", 50, 1, 1)
    if now.hour == 22 and now.minute == 0:
        log.info("It is {0!s}:{1!s}, deactivated Balkonbeleuchtung.".format(now.hour, now.minute))
        Data.tinkerforge_connection.switch_socket("nXN", 50, 1, 0)


def wakeup_rule():
    wakup = datetime.datetime.strptime(Data.wakeup_time, "%H:%M")
    now = datetime.datetime.now()
    if wakup.minute >= 10:
        time_until_wakup = wakup.minute - now.minute
        if wakup.hour == now.hour and time_until_wakup == 10:
            log.info("Beginning to light up the bedroom, wake up!")
            for i in range(15):
                Data.tinkerforge_connection.dim_socket("nXN", 25, 1, i)
                time.sleep(30)
    else:
        log.warn("We don't support wakup times with minute <10 currently.")


##########################################################################################
# The Webserver
##########################################################################################


class Webserver(object):
    """Every api the webserver provides should be in its own class. The webserver shall
    initialize these classes. Then, cherrypy mounts the webserver and the subclasses at
    the desired endpoints."""

    # initialize subclasses
    def __init__(self):
        self.socket = self.Socket()
        self.rule = self.Rule()
        self.additional_information = self.AdditionalInformation()

    # entrypoint to webpage
    @cherrypy.expose
    def index(self):
            raise cherrypy.HTTPRedirect("/static")

    class Socket:
        """Webserver class to control sockets and dimmer."""

        @cherrypy.expose
        def list(self):
            sockets = self.create_socket_entry("Schreibtischlampe", 30, 3)
            sockets += self.create_socket_entry("Hintergrundbeleuchtung", 30, 2)
            sockets += self.create_socket_entry("Laterne", 31, 2)
            sockets += self.create_dim_entry("Nachtlicht", 25, 1)
            sockets += self.create_socket_entry("Balkonbewässerung", 50, 1)
            return sockets

        @cherrypy.expose
        def switch(self, address=-1, unit=-1, state=-1):
            if address == -1 or unit == -1 or state == -1:
                return "Invalid information: {0!s}, {1!s}, {2!s}.".format(address, unit, state)
            Data.tinkerforge_connection.switch_socket("nXN", int(address), int(unit), int(state))
            log.info("Sending signal to switch socket {0!s}-{1!s} to {2!s}.".format(address, unit, state))

        @cherrypy.expose
        def dim(self, address=-1, unit=-1, dim_value=-1):
            if address == -1 or unit == -1 or dim_value == -1:
                return "Invalid information: {0!s}, {1!s}, {2!s}.".format(address, unit, dim_value)
            Data.tinkerforge_connection.dim_socket("nXN", int(address), int(unit), int(dim_value))
            log.info("Tried to dim socket {0!s}-{1!s} to {2!s}.".format(address, unit, dim_value))

        @staticmethod
        def create_socket_entry(name, address, unit):
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

        @staticmethod
        def create_dim_entry(name, address, unit):
            item_id = str(address) + "_" + str(unit)
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
            """.format(n=name, a=str(address), u=str(unit), i=item_id)

    class Rule:
        """Webserver class to control rules."""

        @cherrypy.expose
        def list(self):
            rules = ""
            for index in range(0, len(Data.active_rules)):
                rules += self.create_rule_entry(index)
            return rules

        @cherrypy.expose
        def toggle_rule_keep_alive(self, position, keep_alive):
            position = int(position)
            if 0 <= position < len(Data.active_rules):
                if keep_alive == "false":
                    Data.active_rules[position].deactivate_rule()
                else:
                    Data.active_rules[position].activate_rule()
            else:
                log.warn("No rule at position " + str(position))

        @staticmethod
        def create_rule_entry(position):
            name = Data.active_rules[position].tname
            if Data.active_rules[position].keep_alive:
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

    class AdditionalInformation:
        """Webserver class to provide additional information."""

        @cherrypy.expose
        def connected_devices(self):
            if len(Data.tinkerforge_connection.current_entries) == 0:
                return "<li>Keine Geräte angeschlossen</li>"
            string = ""
            for key in Data.tinkerforge_connection.current_entries:
                string += ("<li>{0} ({1})</li>"
                           .format(key, Data.tinkerforge_connection.current_entries[key]))
            return string

        @cherrypy.expose
        def amm_illuminance(self):
            return (
                "<li id='information_amm_illuminance'>Aktuelle Helligkeit (amm): " +
                str(Data.tinkerforge_connection.get_illuminance("amm")) + " Lux</li>"
            )

        @cherrypy.expose
        def bvg(self):
            array = Data.bvg.call()
            if array is None:
                return "<li>Keine Abfahrtzeiten verfügbar</li>"
            string = ""
            for entry in array:
                string += "<li>{0} -> {1} ({2})</li>".format(entry[3], entry[1], entry[2])
            return string

        @cherrypy.expose
        def set_wakeup_time(self, wakeup_time):
            Data.wakeup_time = wakeup_time
            # TODO make sure that is has the right format
            log.info("Set wakeup time to {0}.".format(wakeup_time))

        @cherrypy.expose
        def get_wakeup_time(self):
            return Data.wakeup_time


##########################################################################################
# The Entrypoint of the Application
##########################################################################################


if __name__ == '__main__':
    # start all needed modules
    Data.tinkerforge_connection = TinkerforgeConnection("192.168.0.248")
    Data.bvg = BVG("Seesener Str. (Berlin)", limit=4)

    # load all rules
    Data.active_rules.append(Rule(tname="Bewässerungsregel (9 und 19 Uhr)", rule_logic=watering_rule, sleep_time=50))

    # start the webserver and configure logging
    cherrypy.engine.unsubscribe('graceful', cherrypy.log.reopen_files)
    logging.config.dictConfig(log_conf)
    webserver = Webserver()
    cherrypy.tree.mount(webserver.socket, '/socket', conf)
    cherrypy.tree.mount(webserver.rule, '/rule', conf)
    cherrypy.tree.mount(webserver.additional_information, '/additional_information', conf)
    cherrypy.quickstart(webserver, '/', conf)
