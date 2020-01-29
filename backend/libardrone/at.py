# Copyright (c) 2011 Bastian Venthur, 2016 Andreas Bresser
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
low level AT Commands
"""
import struct
import socket

ARDRONE_COMMAND_PORT = 5556

def at_ref(addr, seq, takeoff, emergency=False):
    """
    Basic behaviour of the drone: take-off/landing, emergency stop/reset)

    Parameters:
    seq -- sequence number
    takeoff -- True: Takeoff / False: Land
    emergency -- True: Turn off the engines
    """
    p = 0b10001010101000000000000000000
    if takeoff:
        p += 0b1000000000
    if emergency:
        p += 0b0100000000
    at(addr, "REF", seq, [p])

def at_pcmd(addr, seq, progressive, lr, fb, vv, va):
    """
    Makes the drone move (translate/rotate).

    Parameters:
    seq -- sequence number
    progressive -- True: enable progressive commands, False: disable (i.e.
        enable hovering mode)
    lr -- left-right tilt: float [-1..1] negative: left, positive: right
    fb -- front-back tilt: float [-1..1] negative: forwards, positive:
        backwards
    vv -- vertical speed: float [-1..1] negative: go down, positive: rise
    va -- angular speed: float [-1..1] negative: spin left, positive: spin
        right

    The above float values are a percentage of the maximum speed.
    """
    at(addr, "PCMD", seq, [int(progressive), float(lr), float(fb), float(vv), float(va)])

def at_ftrim(addr, seq):
    """
    Tell the drone it's lying horizontally.

    Parameters:
    seq -- sequence number
    """
    at(addr, "FTRIM", seq, [])

def at_config(addr, seq, option, value):
    """Set configuration parameters of the drone."""
    at(addr, "CONFIG", seq, [str(option), str(value)])

def at_config_ids(addr, seq, value):
    """Set configuration parameters of the drone."""
    at(addr, "CONFIG_IDS", seq, value)

def at_ctrl(addr, seq, num):
    """Ask the parrot to drop its configuration file"""
    at(addr, "CTRL", seq, [num, 0])

def at_comwdg(addr, seq):
    """
    Reset communication watchdog.
    """
    at(addr, "COMWDG", seq, [])

def at_aflight(addr, seq, flag):
    """
    Makes the drone fly autonomously.

    Parameters:
    seq -- sequence number
    flag -- Integer: 1: start flight, 0: stop flight
    """
    at(addr, "AFLIGHT", seq, [flag])

##def at_pwm(addr, seq, m1, m2, m3, m4):
##    """
##    Sends control values directly to the engines, overriding control loops.
##
##    Parameters:
##    seq -- sequence number
##    m1 -- front left command
##    m2 -- fright right command
##    m3 -- back right command
##    m4 -- back left command
##    """
##    # FIXME: what type do mx have?
##    raise NotImplementedError()
##
##def at_led(addr, seq, anim, f, d):
##    """
##    Control the drones LED.
##
##    Parameters:
##    seq -- sequence number
##    anim -- Integer: animation to play
##    f -- ?: frequence in HZ of the animation
##    d -- Integer: total duration in seconds of the animation
##    """
##    pass

def at_anim(addr, seq, anim, d):
    """
    Makes the drone execute a predefined movement (animation).

    Parameters:
    seq -- sequcence number
    anim -- Integer: animation to play
    d -- Integer: total duration in sections of the animation
    """
    at(addr, "ANIM", seq, [anim, d])

def at(addr, command, seq, params):
    """
    Parameters:
    command -- the command
    seq -- the sequence number
    params -- a list of elements which can be either int, float or string
    """
    param_str = ''
    for p in params:
        if type(p) == int:
            param_str += ",%d" % p
        elif type(p) == float:
            param_str += ",%d" % f2i(p)
        elif type(p) == str:
            param_str += ',"' + p + '"'
    msg = "AT*%s=%i%s\r" % (command, seq, param_str)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(msg.encode("utf-8"), (addr, ARDRONE_COMMAND_PORT))

def f2i(f):
    """Interpret IEEE-754 floating-point value as signed integer.

    Arguments:
    f -- floating point value
    """
    return struct.unpack('i', struct.pack('f', f))[0]
