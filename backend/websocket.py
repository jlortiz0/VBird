#!/usr/bin/python3

import json
import math
import signal
import platform
import asyncio
import traceback
import serial
import websockets

persist = {}
async def connection_handler(sock, _):
    try:
        while True:
            msg = await sock.recv()
            print("get "+msg)
            msg = json.loads(msg)
            if msg["method"] == "calcPoints":
                lines = []
                for x in msg["line"]:
                    x = x.split(' ')
                    lines.append((-float(x[0][:-1])/float(x[2][:-1]),
                                  float(x[4])/float(x[2][:-1])))
                persist["lines"] = lines
                output = []
                d = msg["dist"]
                for point in msg["points"]:
                    output.append([point[3]])
                    output[-1].append((point[0]+d, point[1]))
                    output[-1].append((point[0]+d, point[1]+d))
                    output[-1].append((point[0], point[1]+d))
                await sock.send(json.dumps({
                    "method":   "pointsList",
                    "points":   output
                    }))
            elif msg["method"] == "start":
                RTLOG.set_sock(sock)
                RTLOG.set_and_reset(persist["slope"], persist["yint"])
            elif msg["method"] == "getDronePos":
                await sock.send(json.dumps({
                    "method":   "dronePos",
                    "x":        RTLOG.masterPos[0],
                    "y":        RTLOG.masterPos[1],
                    "z":        RTLOG.masterPos[2],
                    }))
            elif msg["method"] == "ping":
                await sock.send("{\"method\": \"logData\", \"message\": \"pong\"}")
            elif msg["method"] == "stop":
                await sock.close()
                raise KeyboardInterrupt
            else:
                await sock.send(build_err("No such method "+msg["method"], 1))
    except websockets.exceptions.ConnectionClosedOK:
        pass
    except websockets.exceptions.WebSocketException:
        traceback.print_exc()
    except Exception:
        traceback.print_exc()

def build_err(msg, code):
    print("Error: "+msg+"\nCode: "+str(code))
    return "{{\"method\": \"error\", \"message\": \"{0}\", \"code\": {1}}}".format(msg, code)

TOLERANCE = 0.005
class RealTimeLog:
    def __init__(self):
        self.slope = 1
        self.yint = 0
        if platform.system() == 'Windows':
            self.port = serial.Serial("COM4", 115200)
        else:
            self.port = serial.Serial('/dev/ttyUSB0', 115200)
        self.total = -2
        self.deviate = 0
        self.sock = None
        self.masterSerial = None
        self.masterPos = (0, 0, 0)

    def set_eqn(self, slope, yint):
        self.slope = slope
        self.yint = yint

    def stdev(self):
        return math.sqrt(self.deviate**2/total)
    
    def reset(self):
        stdev = self.stdev()
        self.total = -2
        self.deviate = 0
        self.port.reset_input_buffer()
        return stdev

    def set_and_reset(self, slope, yint):
        self.set_eqn(slope, yint)
        return self.reset()

    def set_sock(self, sock=None):
        self.sock = sock

    async def run(self):
        await asyncio.sleep(1)
        self.port.write(b'reset\r\n\r\n')
        self.port.flush()
        await asyncio.sleep(2)
        self.port.write(b'lep\n')
        self.port.flush()
        await asyncio.sleep(0.25)
        self.port.reset_input_buffer()
        while True:
            avg = [0, 0, 0]
            count = 0
            while self.port.in_waiting:
                data = self.port.read_until().decode().split(',')
                if data[0] == "POS":
                    data = tuple(map(float, data[2:6]))
                    #[identifier, x, y, z]
                    if self.masterSerial == data[0]:
                        self.masterPos = data[1:]
                    for i in range(len(data)-1):
                        avg[i] += data[i+1]
                    count += 1
            avg = tuple(map(lambda x: x/count, avg))
            intended = self.slope * avg[0] + self.yint
            if abs(avg[1]-intended) > TOLERANCE:
                print("Anomaly detected! "+str(round(avg[1]-intended, 3))+" m off!")
            else:
                print("On track.")
            if self.sock:
                await self.sock.send(json.dumps({
                    "method":   "dronePos",
                    "x":        avg[0],
                    "y":        avg[1],
                    "z":        avg[2]
                }))
            self.deviate += avg[1]-intended
            self.total += 1
            await asyncio.sleep(0.25)           

RTLOG = RealTimeLog()
signal.signal(signal.SIGINT, signal.default_int_handler)
start_server = websockets.serve(connection_handler, "localhost", 7777)
asyncio.ensure_future(start_server)
asyncio.ensure_future(RTLOG.run())
try:
    asyncio.get_event_loop().run_forever()
except KeyboardInterrupt:
    pass
