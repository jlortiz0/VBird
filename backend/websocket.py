#!/usr/bin/python3

import json
import math
import signal
import asyncio
import traceback
import serial
import websockets
import serial.tools.list_ports

persist = {"lines":[]}
async def connection_handler(sock, _):
    try:
        while True:
            msg = await sock.recv()
            print("get "+msg)
            msg = json.loads(msg)
            if msg["method"] == "calcPoints":
                lines = []
                for i,x in enumerate(msg["lines"]):
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
        self.port = serial.Serial(serial.tools.list_ports.comports()[0].device, 115200)
        self.total = -2
        self.deviate = 0
        self.sock = None
        self.masterSerial = "ABCD"
        self.masterPos = (0, 0, 0)
        self.debug = False

    def stdev(self):
        return math.sqrt(self.deviate**2/self.total)
    
    def reset(self):
        stdev = self.stdev()
        self.total = -2
        self.deviate = 0
        self.port.reset_input_buffer()
        if self.debug:
            if persist["lines"]:
                msg = "in {} {} "+str(persist["vel"])+" "+str(persist["height"])+"\n"
                msg = msg.format(persist["lines"][0][0], persist["lines"][0][1])
                self.port.write(msg.encode())
            else:
                self.port.write(b'reset\r\nlep\n')
            self.port.flush()
            self.port.reset_input_buffer()
        return stdev

    def set_sock(self, sock=None):
        self.sock = sock

    async def run(self):
        await asyncio.sleep(2)
        self.port.write(b'reset\r\n\r\n')
        self.port.flush()
        await asyncio.sleep(2)
        if (self.port.read(2) == b'jj'):
            print("Debug mode")
            self.debug = True
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
                    data = (data[2],)+tuple(map(float, data[3:6]))
                    #[identifier, x, y, z]
                    if self.masterSerial == data[0]:
                        for i in range(len(data)-1):
                            avg[i] += data[i+1]
                        count += 1
            if not count:
                await asyncio.sleep(0.25)
                continue
            avg = tuple(map(lambda x: x/count, avg))
            if self.sock and self.masterPos != avg:
                await self.sock.send(json.dumps({
                    "method":   "dronePos",
                    "x":        avg[0],
                    "y":        avg[1],
                    "z":        avg[2]
                }))
            self.masterPos = avg
            if persist["lines"]:
                intended = persist["lines"][0][0] * avg[0] + persist["lines"][0][1]
                self.deviate += avg[1]-intended
                self.total += 1
                if abs(avg[1]-intended) > TOLERANCE:
                    print("Anomaly detected! "+str(round(avg[1]-intended, 3))+" m off!")
                else:
                    print("On track.")
                    if avg[0] >= persist["lines"][0][2]:
                        del persist["lines"][0]
                        print("Line completed. Average deviation "+str(self.reset()))
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
