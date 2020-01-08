#!/usr/bin/python3

import math
#import serial

#use lec, not les
#it's easier to process
#using the fake line y=2x+3
SLOPE = 2
YINT = 3
#Tolerance of 0.25 off
#This is in Decawave units, not percentage
TOLERANCE = 0.25
TOTAL = 0
DEVIATE = 0
with open('testUWBData.log') as f:
    for x in f.readlines():
        data = x.split(',')
        if data[0] == 'DIST' and 'POS' in data:
            data = tuple(map(float, data[data.index('POS')+1:][:2]))
            #data is now [x, y, z]
            #How are we supposed to know what the x value is?
            intended = SLOPE * data[0] + YINT
            #Placeholder z value
            h = math.hypot(data[0]-TOTAL, data[1]-intended, 0)
            if h > TOLERANCE:
                print("Anomoly detected! "+str(round(h, 3))+" units off!")
            #This gets messy while testing
            #else:
                #print("On track.")
            DEVIATE += h
            TOTAL += 1
            
print("Complete. Average deviation was "+str(round(DEVIATE/TOTAL, 3))+" units")
