#!/usr/bin/python3

import math

class Shape(object):

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
        MPOSA = [0, 0, 0]
        return MPOSA

    def setCurrPosMasterA(self, APos):
        self.MAX = APos[0]
        self.MAY = APos[1]
        self.MAZ = APos[2]

    def printCurrPosMasterA(self, APos):
        print("Current Starting Position A is: ("+",".join(map(str, APos))+")")

    def askFinalDest(self):
        MPOSB = [0, 0, 0]
        X = float(input("What is the final X point of the Master Drone?: "))
        MPOSB[0] = X
        self.MBX = X
        Y = float(input("What is the final Y point of the Master Drone?: "))
        MPOSB[1] = Y
        self.MBY = Y
        Z = float(input("What is the final Z point of the Master Drone?: "))
        MPOSB[2] = Z
        self.MBZ = Z
        print("The swarm will fly to this Point B: ("+",".join(map(str, MPOSB))+")")
        return MPOSB

    # calculates the dist for master drone same for all other drones but formation needs to be known
    def setDirectDistM(self):
        sqrtVal = (self.MAX - self.MBX)**2 + (self.MAY - self.MBY)**2
        # print sqrtVal
        self.directDistM = math.sqrt(sqrtVal)

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
            dir1 = "north"
        elif yVal < 0:
            dir1 = "south"
        if xVal > 0:
            dir2 = "east"
        elif xVal < 0:
            dir2 = "west"
        return (str(angle) + " degrees " + dir1 + dir2)

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
        self.numDrones = int(input("How many drones are there? "))
        if self.numDrones == 1:
            #I hate this
            c = Circle()
            self.__class__ = c.__class__
            self.__dict__ = c.__dict__
        return self.numDrones

    def checkFormation(self, numDrones):
        raise NotImplementedError

    def printShriKishoriKishore(self):
        raise NotImplementedError

# ask radius of pcta/deca/hexa gon..
# ask # of drones DONE IN SHAPE PARENT CLASS
class Circle(Shape):
    def printShriKishoriKishore(self):
        print("ShriKishoriKishore")

    def checkFormation(self, numDrones):
        return True
