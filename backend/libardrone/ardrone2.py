# Copyright (c) 2011 Bastian Venthur
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


"""
Python library for the AR.Drone.

V.1 This module was tested with Python 2.6.6 and AR.Drone vanilla firmware 1.5.1.
V.2.alpha
"""

import logging
import sys
import threading
import multiprocessing
import time
import numpy as np

import arnetwork
import at

SESSION_ID = "943dac23"
USER_ID = "36355d78"
APP_ID = "21d958e4"


class ARDrone2(object):
    """Instanciate this class to control your drone and receive decoded navdata."""

    def __init__(self, addr="192.168.1.1"):

        self.seq_nr = 1
        self.timer_t = 0.2
        self.com_watchdog_timer = threading.Timer(self.timer_t, self.commwdg)
        self.lock = threading.Lock()
        self.speed = 0.2
        self.addr = addr

        time.sleep(0.5)
        self.config_ids_string = [SESSION_ID, USER_ID, APP_ID]
        self.configure_multisession(SESSION_ID, USER_ID, APP_ID, self.config_ids_string)
        self.set_session_id (self.config_ids_string, SESSION_ID)
        time.sleep(0.5)
        self.set_profile_id(self.config_ids_string, USER_ID)
        time.sleep(0.5)
        self.set_app_id(self.config_ids_string, APP_ID)

        self.last_command_is_hovering = True
        self.com_pipe, com_pipe_other = multiprocessing.Pipe()

        self.navdata = dict.fromkeys(('ctrl_state', 'battery', 'theta', 'phi', 'psi', 'altitude', 'vx', 'vy', 'vz', 'num_frames'), 0)

        self.network_process = arnetwork.ARDroneNetworkProcess(com_pipe_other, self)
        self.network_process.start()

        time.sleep(1)

        self.at(at.at_config_ids, self.config_ids_string)
        self.at(at.at_config, "general:navdata_demo", "TRUE")


    def takeoff(self):
        """Make the drone takeoff."""
        self.at(at.at_ftrim)
        self.at(at.at_config, "control:altitude_max", "20000")
        self.at(at.at_ref, True)

    def land(self):
        """Make the drone land."""
        self.at(at.at_ref, False)

    def hover(self):
        """Make the drone hover."""
        self.at(at.at_pcmd, False, 0, 0, 0, 0)

    def move_left(self):
        """Make the drone move left."""
        self.at(at.at_pcmd, True, -self.speed, 0, 0, 0)

    def move_right(self):
        """Make the drone move right."""
        self.at(at.at_pcmd, True, self.speed, 0, 0, 0)

    def move_up(self):
        """Make the drone rise upwards."""
        self.at(at.at_pcmd, True, 0, 0, self.speed, 0)

    def move_down(self):
        """Make the drone decent downwards."""
        self.at(at.at_pcmd, True, 0, 0, -self.speed, 0)

    def move_forward(self):
        """Make the drone move forward."""
        self.at(at.at_pcmd, True, 0, -self.speed, 0, 0)

    def move_backward(self):
        """Make the drone move backwards."""
        self.at(at.at_pcmd, True, 0, self.speed, 0, 0)

    def turn_left(self):
        """Make the drone rotate left."""
        self.at(at.at_pcmd, True, 0, 0, 0, -self.speed)

    def turn_right(self):
        """Make the drone rotate right."""
        self.at(at.at_pcmd, True, 0, 0, 0, self.speed)

    def reset(self):
        """Toggle the drone's emergency state."""
        # Enter emergency mode
        self.at(at.at_ref, False, True)
        self.at(at.at_ref, False, False)
        # Leave emergency mode
        self.at(at.at_ref, False, True)

    def trim(self):
        """Flat trim the drone."""
        self.at(at.at_ftrim)

    def set_speed(self, speed):
        """Set the drone's speed.

        Valid values are floats from [0..1]
        """
        self.speed = speed

    def at(self, cmd, *args, **kwargs):
        """Wrapper for the low level at commands.

        This method takes care that the sequence number is increased after each
        at command and the watchdog timer is started to make sure the drone
        receives a command at least every second.
        """
        self.lock.acquire()
        self.com_watchdog_timer.cancel()
        cmd(self.addr, self.seq_nr, *args, **kwargs)
        self.seq_nr += 1
        self.com_watchdog_timer = threading.Timer(self.timer_t, self.commwdg)
        self.com_watchdog_timer.start()
        self.lock.release()

    def move(self, lr, fb, ud, turn):
    	self.at(at.at_pcmd, True, float(lr), float(fb), float(ud), float(turn))

    def configure_multisession(self, session_id, user_id, app_id, config_ids_string):
        self.at(at.at_config, "custom:session_id", session_id)
        self.at(at.at_config, "custom:profile_id", user_id)
        self.at(at.at_config, "custom:application_id", app_id)

    def set_session_id (self, config_ids_string, session_id):
        self.at(at.at_config_ids, config_ids_string)
        self.at(at.at_config, "custom:session_id", session_id)

    def set_profile_id (self, config_ids_string, profile_id):
        self.at(at.at_config_ids, config_ids_string)
        self.at(at.at_config, "custom:profile_id", profile_id)

    def set_app_id (self, config_ids_string, app_id):
        self.at(at.at_config_ids, config_ids_string)
        self.at(at.at_config, "custom:application_id", app_id)

    def commwdg(self):
        """Communication watchdog signal.

        This needs to be send regulary to keep the communication w/ the drone
        alive.
        """
        self.at(at.at_comwdg)

    def halt(self):
        """Shutdown the drone.

        This method does not land or halt the actual drone, but the
        communication with the drone. You should call it at the end of your
        application to close all sockets, pipes, processes and threads related
        with this object.
        """
        self.lock.acquire()
        self.com_watchdog_timer.cancel()
        self.com_pipe.send('die!')
        self.network_process.terminate()

        #self.network_process.join()
        self.lock.release()

    def get_navdata(self):
        return self.navdata

    def set_navdata(self, navdata):
        self.navdata = navdata

    def apply_command(self, command):
        available_commands = ["emergency",
        "land", "takeoff", "move_left", "move_right", "move_down", "move_up",
        "move_backward", "move_forward", "turn_left", "turn_right", "hover"]
        if command not in available_commands:
            logging.error("Command %s is not a recognized command" % command)

        if command != "hover":
            self.last_command_is_hovering = False
        if (command == "emergency"):
            self.reset()
        elif (command == "land"):
            self.land()
            self.last_command_is_hovering = True
        elif (command == "takeoff"):
            self.takeoff()
            self.last_command_is_hovering = True
        elif (command == "move_left"):
            self.move_left()
        elif (command == "move_right"):
            self.move_right()
        elif (command == "move_down"):
            self.move_down()
        elif (command == "move_up"):
            self.move_up()
        elif (command == "move_backward"):
            self.move_backward()
        elif (command == "move_forward"):
            self.move_forward()
        elif (command == "turn_left"):
            self.turn_left()
        elif (command == "turn_right"):
            self.turn_right()
        elif (command == "hover" and not self.last_command_is_hovering):
            self.hover()
            self.last_command_is_hovering = True
