#!/usr/bin/python3

import time
import math
import asyncio
import serial
import serial.tools.list_ports
from fuentes import Tello

TOLERANCE = 0.25
HEIGHT = 0.5
#Horizontal, y=3.4 to x=5
LINES = [(0, 3.4, 4)]
VEL = 30
port = serial.Serial(serial.tools.list_ports.comports()[0].device, 115200)
total = 0
deviate = []
drone = Tello()
log = open('logs/rtserial.log', 'w')
sTime = time.time()

def stdev():
    final = 0
    for x in deviate[2:-2]:
        final += math.sqrt(x**2/total)
    return final

def reset():
    global total, deviate
    std = stdev()
    total = 0
    deviate = []
    port.reset_input_buffer()
    log.flush()
    return std

async def run():
    global deviate, total
    if not port.in_waiting:
        port.write(b'lep\r')
        port.flush()
    await asyncio.sleep(0.25)
    await drone.connect()
    port.reset_input_buffer()
    await drone.takeoff()
    log.write("!! LINESTART y = {:.3f}x + {:.3f} x to {:.3f}\n".format(*LINES[0]))
    while True:
        avg = [0, 0, 0]
        count = 0
        while port.in_waiting:
            data = port.read_until().decode().split(',')
            if data[0] == "POS":
                data = (data[2],)+tuple(map(float, data[3:6]))
                #[identifier, x, y, z]
                #if self.masterSerial == data[0]:
                for i in range(len(data)-1):
                    avg[i] += data[i+1]
                count += 1
        if count:
            avg = tuple(map(lambda x: x/count, avg))
        if LINES:
            intended = LINES[0][0] * avg[0] + LINES[0][1]
            log.write('{:.3f} {:.3f} {:.3f} {:.3f}\n'.format(time.time()-sTime, avg[0], avg[1], intended))
            deviate.append(abs(intended - avg[1]))
            total += 1
            #Setup some vars to make it more readable
            #Some are multiplied by 100 as drone uses cm, not m
            #Distance between current point and target point
            dsty = 100 * (intended - avg[1])
            dstx = 100 * (LINES[0][2] - avg[0])
            print(dstx, dsty)
            #Intended height and current height
            #intH = HEIGHT * 100
            #curH = await drone.get_height()
            #Try to normalize height first
            #if abs(intH - curH) > 50:
                #drone.send_rc_control(0, 0, max(min(abs(intH - curH), 100), -100), 0)
            if math.hypot(dsty, dstx) > 50:
                if abs(dstx) < abs(dsty):
                    #Calculate the tangent of the triangle formed by dst and dsty
                    tan = math.copysign(dstx/dsty, dstx)
                    #Find the side lengths of similar triangle with the longest side as persist["vel"]
                    #Make sure that we round off as the function only accepts int
                    #Copy signs to ensure we go the right direction
                    drone.send_rc_control(round(tan*VEL), int(math.copysign(VEL, dsty)), 0, 0)
                else:
                    tan = math.copysign(dsty/dstx, dsty)
                    drone.send_rc_control(int(math.copysign(VEL, dstx)), round(tan*VEL), 0, 0)
            #Return to using m
            #if abs(avg[1] - intended) > TOLERANCE:
                #print("Anomaly detected! "+str(round(avg[1]-intended, 3))+" m off!")
            #else:
                #print("On track.")
            if abs(avg[0] - LINES[0][2]) <= TOLERANCE:
                del LINES[0]
                drone.send_rc_control(0, 0, 0, 0)
                deviate = str(reset())
                print("Line completed. Average deviation "+deviate)
                log.write("!! LINEEND {}\n".format(deviate))
                if LINES:
                    log.write("!! LINESTART y = {:.3f}x + {:.3f} x to {:.3f}\n".format(*LINES[0]))
                else:
                    await drone.land()
                    return
        await asyncio.sleep(0.25)

try:
    asyncio.run(run())
except KeyboardInterrupt:
    drone._oldSock.sendto(b'land', drone.address)
log.close()
