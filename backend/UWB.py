#!/usr/bin/python3

import time
import math
import asyncio
import serial
import serial.tools.list_ports
from fuentes import Tello

TOLERANCE = 15*math.sqrt(2)
HEIGHT = 0.5
#Diagonal, y=x to x=3.8
LINES = [(0, 3.4, 7)]
VEL = 20
port = serial.Serial(serial.tools.list_ports.comports()[0].device, 115200)
total = 0
deviate = []
drone = Tello()
log = open('logs/UWBTest.log', 'w')
ANOMTIME = 2

def stdev():
    #final = 0
    #for x in deviate[2:-2]:
        #final += math.sqrt(x**2/total)
    return sum(deviate[2:-2])/(total-4)

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
    await asyncio.sleep(0.5)
    if not port.in_waiting:
        port.write(b'\r\r')
        port.flush()
        await asyncio.sleep(1)
        port.write(b'lep\r')
        port.flush()
    await drone.connect()
    port.reset_input_buffer()
    await drone.takeoff()
    print("Battery: {}%".format(drone.battery))
    sTime = time.time()
    log.write("!! "+str(sTime))
    log.write("!! LINESTART y = {:.3f}x + {:.3f} x to {:.3f}\n".format(*LINES[0]))
    mrPos = (0, 0, 0)
    didAnom = True
    didAnom2 = True
    while True:
        if ANOMTIME < (time.time() - sTime) and not didAnom:
            print("Anomaly create: moving drone -45 cm y!")
            await drone.move_back(45)
            port.reset_input_buffer()
            await asyncio.sleep(0.25)
            didAnom = True
            print("resuming")
        if ANOMTIME+1 < (time.time() - sTime) and not didAnom2:
            print("Anomaly create: moving drone -45 cm y!")
            await drone.move_back(45)
            port.reset_input_buffer()
            await asyncio.sleep(0.25)
            didAnom2 = True
            print("resuming")
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
            mrPos = avg
        else:
            avg = mrPos
        if LINES:
            intended = LINES[0][0] * LINES[0][2] + LINES[0][1]
            log.write('{:.3f} {:.3f} {:.3f} {:.3f}\n'.format(time.time()-sTime, avg[0], avg[1], LINES[0][0]*avg[0]+LINES[0][1]))
            deviate.append(abs(LINES[0][0]*avg[0]+LINES[0][1] - avg[1]))
            total += 1
            #Setup some vars to make it more readable
            #Some are multiplied by 100 as drone uses cm, not m
            #Distance between current point and target point
            dsty = 100 * (intended - avg[1])
            dstx = 100 * (LINES[0][2] - avg[0])
            #Intended height and current height
            #intH = HEIGHT * 100
            #curH = drone.height
            #Try to normalize height first
            #if abs(intH - curH) > 50:
                #drone.send_rc_control(0, 0, max(min(abs(intH - curH), 100), -100), 0)
            if math.hypot(dsty, dstx) > TOLERANCE:
                if abs(dstx) < abs(dsty):
                    #Calculate the tangent of the triangle formed by dst and dsty
                    tan = math.copysign(dstx/dsty, dstx)
                    #Find the side lengths of similar triangle with the longest side as persist["vel"]
                    #Make sure that we round off as the function only accepts int
                    #Copy signs to ensure we go the right direction
                    print("{:.3f} {:.3f} {:.3f}".format(dstx, dsty, tan*VEL))
                    drone.send_rc_control(round(tan*VEL), int(math.copysign(VEL, dsty)), 0, 0)
                else:
                    tan = math.copysign(dsty/dstx, dsty)
                    print("{:.3f} {:.3f} {:.3f}".format(dstx, dsty, tan*VEL))
                    drone.send_rc_control(int(math.copysign(VEL, dstx)), round(tan*VEL), 0, 0)
            else:
                #Return to using m
                del LINES[0]
                drone.send_rc_control(0, 0, 0, 0)
                d = str(reset())
                print("Line completed. Average deviation "+d)
                log.write("!! LINEEND {}\n".format(d))
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
log.flush()
log.close()
