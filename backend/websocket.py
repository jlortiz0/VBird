#!/usr/bin/python3

import json
import math
import time
import signal
import asyncio
import traceback
import websockets
import serial
import serial.tools.list_ports
from fuentes import Tello

persist = {"lines":[]}
async def connection_handler(sock, _):
    try:
        while True:
            msg = await sock.recv()
            print("get "+msg)
            msg = json.loads(msg)
            if msg["method"] == "calcPoints":
                lines = []
                for i, x in enumerate(msg["lines"]):
                    x = x.split(' ')
                    #(slope, yint, targetX)
                    lines.append((-float(x[0][:-1])/float(x[2][:-1]),
                                  float(x[4])/float(x[2][:-1]),
                                  msg["points"][i+1][0]))
                persist["lines"] = lines
                output = []
                d = msg["dist"]
                for point in msg["points"]:
                    output.append([point[3]])
                    output[-1].append((point[0]+d, point[1]))
                    output[-1].append((point[0]+d, point[1]+d))
                    output[-1].append((point[0], point[1]+d))
                persist["height"] = msg["height"]
                await sock.send(json.dumps({
                    "method":   "pointsList",
                    "points":   output
                    }))
            elif msg["method"] == "start":
                persist["vel"] = msg["vel"]
                RTLOG.set_sock(sock)
                RTLOG.reset()
                await RTLOG.drone.takeoff()
                RTLOG.log.write("!! LINESTART y = {:.3f}x + {:.3f} x to {:.3f}\n".format(*persist["lines"][0]))
            elif msg["method"] == "getDronePos":
                await sock.send(json.dumps({
                    "method":   "dronePos",
                    "x":        RTLOG.masterPos[0],
                    "y":        RTLOG.masterPos[1],
                    "z":        RTLOG.masterPos[2],
                    }))
            elif msg["method"] == "anomaly":
                await RTLOG.anomaly(msg["dir"])
            elif msg["method"] == "emer":
                await RTLOG.drone.emergency()
            elif msg["method"] == "ping":
                await sock.send("{\"method\": \"logData\", \"message\": \"pong\"}")
            elif msg["method"] == "stop":
                await sock.close()
                raise KeyboardInterrupt
            else:
                await sock.send(build_err("No such method "+msg["method"], 1))
    except websockets.exceptions.ConnectionClosedOK:
        pass
    except Exception:
        traceback.print_exc()

def build_err(msg, code):
    print("Error: "+msg+"\nCode: "+str(code))
    return "{{\"method\": \"error\", \"message\": \"{0}\", \"code\": {1}}}".format(msg, code)

TOLERANCE = 0.25
class RealTimeLog:
    def __init__(self):
        self.port = serial.Serial(serial.tools.list_ports.comports()[0].device, 115200)
        self.total = 0
        self.deviate = 0
        self.sock = None
        #self.masterSerial = "ABCD"
        self.masterPos = (0, 0, 0)
        self.drone = Tello()
        self.log = open('logs/VBirdDebug.log', 'w')

    def stdev(self):
        if self.total < 4:
            return 0
        return sum(self.deviate[2:-2])/(self.total-4)

    async def anomaly(self, direct):
        await self.drone.flip(direct)

    def reset(self):
        stdev = self.stdev()
        self.total = 0
        self.deviate = []
        self.port.reset_input_buffer()
        self.log.flush()
        return stdev

    def set_sock(self, sock=None):
        self.sock = sock

    async def run(self):
        await asyncio.sleep(0.5)
        if not self.port.in_waiting:
            self.port.write(b'lep\n')
            self.port.flush()
        await asyncio.sleep(0.25)
        await self.drone.connect()
        self.time = time.time()
        self.port.read(5)
        while True:
            avg = [0, 0, 0]
            count = 0
            while self.port.in_waiting:
                data = self.port.read_until().decode().split(',')
                if data[0] == "POS":
                    data = (data[2],)+tuple(map(float, data[3:6]))
                    #[identifier, x, y, z]
                    #if self.masterSerial == data[0]:
                    for i in range(len(data)-1):
                        avg[i] += data[i+1]
                    count += 1
            if count:
                avg = tuple(map(lambda x: x/count, avg))
                if self.sock and self.masterPos != avg:
                    await self.sock.send(json.dumps({
                        "method":   "dronePos",
                        "x":        avg[0],
                        "y":        avg[1],
                        "z":        avg[2]
                    }))
                self.masterPos = avg
            else:
                avg = self.masterPos
            if persist["lines"] and self.sock:
                intended = persist["lines"][0][0] * persist["lines"][0][2] + persist["lines"][0][1]
                self.log.write('{:.3f} {:.3f} {:.3f} {:.3f}\n'.format(time.time()-self.time, avg[0], avg[1], intended))
                self.deviate.append(abs(intended - avg[1]))
                self.total += 1
                #Setup some vars to make it more readable
                #Some are multiplied by 100 as drone uses cm, not m
                #Distance between current point and target point
                dsty = 100 * (intended - avg[1])
                dstx = 100 * (persist["lines"][0][2] - avg[0])
                #Intended height and current height
                intH = persist["height"] * 100
                curH = self.drone.height
                #Try to normalize height first
                if abs(intH - curH) > 50:
                    self.drone.send_rc_control(0, 0, max(min(abs(intH - curH), 100), -100), 0)
                elif math.hypot(dsty, dstx) > 50:
                    if abs(dstx) < abs(dsty):
                        #Calculate the tangent of the triangle formed by dst and dsty
                        tan = math.copysign(dstx/dsty, dstx)
                        #Find the side lengths of similar triangle with the longest side as persist["vel"]
                        #Make sure that we round off as the function only accepts int
                        #Copy signs to ensure we go the right direction
                        self.drone.send_rc_control(round(tan*persist["vel"]), int(math.copysign(persist["vel"], dsty)), 0, 0)
                    else:
                        tan = math.copysign(dsty/dstx, dsty)
                        self.drone.send_rc_control(int(math.copysign(persist["vel"], dstx)), round(tan*persist["vel"]), 0, 0)
                #Return to using m
                if math.hypot(avg[1] - intended, avg[0] - persist["lines"][0][2]) <= TOLERANCE:
                    del persist["lines"][0]
                    self.drone.send_rc_control(0, 0, 0, 0)
                    deviate = str(self.reset())
                    print("Line completed. Average deviation "+deviate)
                    self.log.write("!! LINEEND {}\n".format(deviate))
                    if persist["lines"]:
                        self.log.write("!! LINESTART y = {:.3f}x + {:.3f} x to {:.3f}\n".format(*persist["lines"][0]))
                    else:
                        await self.drone.land()
            await asyncio.sleep(0.25)

RTLOG = RealTimeLog()
signal.signal(signal.SIGINT, signal.default_int_handler)
start_server = websockets.serve(connection_handler, "localhost", 7777)
asyncio.ensure_future(start_server)
asyncio.ensure_future(RTLOG.run())
try:
    asyncio.get_event_loop().run_forever()
except KeyboardInterrupt:
    RTLOG.drone._oldSock.sendto(b'land', RTLOG.drone.address)
RTLOG.log.close()
