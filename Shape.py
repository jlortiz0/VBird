#!/usr/bin/env python

import math

class Shape(object):
    def __init__(self):
        pass

    numDrones = 0

    # x, y, z position of Point a for Master Drone
    MAX = 0.0
    MAY = 0.0
    MAZ = 0.0

    # x, y, z position of Point B for Master Drone
    MBX = 0.0
    MBY = 0.0
    MBZ = 0.0
    directDistM = 0.0

    def getCurrPosMasterA(self):
        #  will read only one line of the file for the position of the master drone.. (each drone has specific identity/name in log file) ..keep default for 0 testing
        MPOSA = [None]*3
        MPOSA[0] = 0
        MPOSA[1] = 0
        MPOSA[2] = 0
        return MPOSA

    def setCurrPosMasterA(self, APos):
        self.MAX = APos[0]
        self.MAY = APos[1]
        self.MAZ = APos[2]

    def printCurrPosMasterA(self, APos):
        currPos = "Current Starting Position A is: ("
        for d in APos:
            currPos += str(d) + ","
        currPos += ")"
        print currPos

    def askFinalDest(self):
        MPOSB = [None]*3
        print "What is the final X point of the Master Drone?: "
        X = float(raw_input())
        MPOSB[0] = X
        self.MBX = X
        print "What is the final Y point of the Master Drone?: "
        Y = float(raw_input())
        MPOSB[1] = Y
        self.MBY = Y
        print "What is the final X point of the Master Drone?: "
        Z = float(raw_input())
        MPOSB[2] = Z
        self.MBZ = Z
        print "The swarm will fly to this Point B: (" + str(X) + "," + str(Y) + "," + str(Z) + ")"
        return MPOSB

    # calculates the dist for master drone same for all other drones but formation needs to be known
    def setDirectDistM(self):
        sqrtVal = (self.MAX - self.MBX)**2 + (self.MAY - self.MBY)**2
        # print sqrtVal
        distance = math.sqrt(sqrtVal)
        self.directDistM = distance

    def getDirectDistM(self):
        return self.directDistM

    def getVelocity(self, time):
        dist = self.getDirectDistM()
        return (dist / time)
        # print "What is the desired velocity in (m/s) of the swarm. Enter 0 to skip vel question and enter the time in seconds instead: "
        #         vel = float(raw_input())
        #         if vel == 0:
        # set the GUI for
        #           time = getTime()
        #           return 0
        #         else:
        #           return vel
        #         

    # get the velocity 
    def getTime(self, velocity):
        dist = self.getDirectDistM()
        return (dist / velocity)

    # get the time 
    # def getSlope(self){
    #     dist = getDirectDistM()
    #     return (dist / velocity)
    #
    #
    # def calcLineInt(self, slope, APosAll, BPosAll):
    #     raise NotImplementedError
    #
    # def printLine(self, s, BIntAll);
    #     raise NotImplementedError
    # only 2d so far.. :(
    def calcDirection(self):
        xVal = (self.MBX - self.MAX)
        yVal = (self.MBY - self.MAY)
        angle = self.calcAngle(xVal, yVal)
        dir1 = ""
        dir2 = ""
        if yVal > 0:
            dir1 += "north"
        else:
            dir1 += "south"
        if xVal > 0:
            dir2 += "east"
        else:
            dir2 += "west"
        return (str(angle) + " degrees " + dir1 + " of " + dir2)

    # end of dir method
    def calcAngle(self, xdist, ydist):
        xdist = abs(xdist)
        ydist = abs(ydist)
        return math.degrees(math.atan(ydist / xdist))

    #  slope shd be DEFINED
    # Calc other drone pos shd be DECLARED/abs
    # the direct linear flight path shd be DECLARED/abs
    # num of drones shd be DEFINED 
    # checkFormation DECLARED?
    def setNumDrones(self):
        print "How many drones are there?"
        self.numDrones = int(raw_input())
        return self.numDrones

    def checkFormation(self, numDrones):
        raise NotImplementedError

    def printShriKishoriKishore(self):
        raise NotImplementedError

#  end of class
