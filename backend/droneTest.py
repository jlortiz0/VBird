#!/usr/bin/python3

import math
import asyncio
from fuentes import Tello

drone = Tello()
async def droneByItself():
    await drone.connect()
    await drone.takeoff()
    dsty = 100 * LINES[0][1]
    dstx = 100 * LINES[0][0]
    #Intended height and current height
    for _ in range(12):
        #intH = HEIGHT * 100
        #curH = int((await drone.get_height())[:-2]) * 10
        #if abs(intH - curH) > 20:
            #drone.send_rc_control(0, 0, max(min(abs(intH - curH), 100), -100), 0)
        if math.hypot(dsty, dstx):
            print(dsty, dstx)
            if abs(dstx) < abs(dsty):
                #Calculate the tangent of the triangle formed by dst and dsty
                tan = math.copysign(dstx/dsty, dstx)
                #Find the side lengths of similar triangle with the longest side as 100
                #Make sure that we round off as the function only accepts int
                #Copy signs to ensure we go the right direction
                drone.send_rc_control(round(tan*SPD), int(math.copysign(SPD, dsty)), 0, 0)
            else:
                tan = math.copysign(dsty/dstx, dsty)
                drone.send_rc_control(int(math.copysign(SPD, dstx)), round(tan*SPD), 0, 0)
        await asyncio.sleep(0.25)
    drone.send_rc_control(0, 0, 0, 0)
    await drone.land()

LINES = [
    #Diagonal, y=x
    (1, 1)
]
HEIGHT = 1
SPD = 30
try:
    asyncio.run(droneByItself())
except KeyboardInterrupt:
    drone._oldSock.sendto(b"land", drone.address)
