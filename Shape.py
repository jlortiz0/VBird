#!/usr/bin/env python
""" generated source for module Shape """
# 
#  * Abstract class Shape - write a description of the class here
#  *
#  * @author Jyoti Rani
#  * @version 0.1 11/07/19
#  
import java.util.Scanner

class Shape(object):
    """ generated source for class Shape """
    def __init__(self):
        """ generated source for method __init__ """

    readIn = Scanner(System.in_)
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
        """ generated source for method getCurrPosMasterA """
        #  will read only one line of the file for the position of the master drone.. (each drone has specific identity/name in log file) ..keep default for 0 testing
        MPOSA = [None]*3
        MPOSA[0] = 0
        MPOSA[1] = 0
        MPOSA[2] = 0
        return MPOSA

    def setCurrPosMasterA(self, APos):
        """ generated source for method setCurrPosMasterA """
        self.MAX = APos[0]
        self.MAY = APos[1]
        self.MAZ = APos[2]

    def printCurrPosMasterA(self, APos):
        """ generated source for method printCurrPosMasterA """
        currPos = "Current Starting Position A is: ("
        for d in APos:
            currPos += d + ","
        currPos += ")"
        print currPos

    def askFinalDest(self):
        """ generated source for method askFinalDest """
        MPOSB = [None]*3
        print "What is the final X point of the Master Drone?: "
        X = self.readIn.nextDouble()
        MPOSB[0] = X
        self.MBX = X
        print "What is the final Y point of the Master Drone?: "
        Y = self.readIn.nextDouble()
        MPOSB[1] = Y
        self.MBY = Y
        print "What is the final X point of the Master Drone?: "
        Z = self.readIn.nextDouble()
        MPOSB[2] = Z
        self.MBZ = Z
        print "The swarm will fly to this Point B: (" + X + "," + Y + "," + Z + ")"
        return MPOSB

    # calculates the dist for master drone same for all other drones but formation needs to be known
    def setDirectDistM(self):
        """ generated source for method setDirectDistM """
        sqrtVal = Math.pow((self.MAX - self.MBX), 2) + Math.pow((self.MAY - self.MBY), 2)
        # print sqrtVal;
        distance = Math.pow(sqrtVal, 0.5)
        self.directDistM = distance

    def getDirectDistM(self):
        """ generated source for method getDirectDistM """
        return self.directDistM

    def getVelocity(self, time):
        """ generated source for method getVelocity """
        dist = self.getDirectDistM()
        return (dist / time)
        # System.out.print("What is the desired velocity in (m/s) of the swarm. Enter 0 to skip vel question and enter the time in seconds instead: ");
        #         double vel = readIn.nextDouble();
        #         if(vel == 0){
        # set the GUI for
        #           double time = getTime();
        #           return 0;
        #         }
        #         else{
        #           return vel;
        #         }
        #         

    # get the velocity 
    def getTime(self, velocity):
        """ generated source for method getTime """
        dist = self.getDirectDistM()
        return (dist / velocity)

    # get the time 
    # public double getSlope(){
    #         double dist = getDirectDistM();
    #         return (dist/velocity);
    #       }
    #       
    # public abstract calcLineInt(double slope, double APosAll[], double BPosAll[]);
    #     public abstract printLine(double s, double BIntAll);
    #     
    # only 2d so far.. :(
    def calcDirection(self):
        """ generated source for method calcDirection """
        xVal = (self.MBX - self.MAX)
        yVal = (self.MBY - self.MBY)
        angle = calcAngle(xVal, yVal)
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
        return (angle + " degrees " + dir1 + " of " + dir2)

    # end of dir method
    def calcAngle(self, xdist, ydist):
        """ generated source for method calcAngle """
        xdist = Math.abs(xdist)
        ydist = Math.abs(ydist)
        return Math.atan(ydist / xdist)

    #  slope shd be DEFINED
    # Calc other drone pos shd be DECLARED/abs
    # the direct linear flight path shd be DECLARED/abs
    # num of drones shd be DEFINED 
    # checkFormation DECLARED?
    def setNumDrones(self):
        """ generated source for method setNumDrones """
        print "How many drones are there?"
        self.numDrones = readIn.nextInt()
        return self.numDrones

    def checkFormation(self, numDrones):
        """ generated source for method checkFormation """

    def printShriKishoriKishore(self):
        """ generated source for method printShriKishoriKishore """

#  end of class

