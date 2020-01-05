#!/usr/bin/env python

import math
from Shape import Shape
from Circle import Circle
from Rectangle import Rectangle
from Square import Square
from Triangle import Triangle

class Main(object):
    form = Shape()

    # public static int numDrones = 0;
    @classmethod
    def main(cls, args):
        print math.atan((4 / 3))
        cls.askFormation()
        cls.handleNumDrones()
        # get Master Drone's A Point Position MAPos[]
        MAPos = cls.form.getCurrPosMasterA()
        cls.form.setCurrPosMasterA(MAPos)
        cls.form.printCurrPosMasterA(MAPos)
        # get Master Drone's B Point Position MAPos[]
        MPOSB = cls.form.askFinalDest()
        cls.form.setDirectDistM()
        dist = cls.form.getDirectDistM()
        print "The direct distance to Point B is: " + str(dist) + " meters"
        print "What is the desired velocity in m/s, of the swarm. Enter 0 to skip vel question and enter the time in seconds instead: "
        vel = float(raw_input())
        if vel == 0:
            print "What is the desired duration of flight in seconds?",
            time = float(raw_input())
            # update teh GUI with the time value
            calcVel = cls.form.getVelocity(time)
            print "The calculated velocity is: " + str(calcVel) + " m/s",
        else:
            calcTime = cls.form.getTime(vel)
            print "The calculated time is: " + str(calcTime) + "seconds"
        print cls.form.calcDirection()
        cls.form.printShriKishoriKishore()

    #  end of main method
    @classmethod
    def askFormation(cls):
        print "\nSquare\t1\nRectangle\t2\nCircle\t3\nTriangle\t4\nHexagon\t5\n\nEnter the number corresponding to the formation you want to choose: "
        val = int(raw_input())
        # switch case to assign inheritance and proper methods corresponding to formation chosen
        if val==1:
            cls.form = Square()
            # call functions particular to this class? 
        elif val==2:
            cls.form = Rectangle()
        elif val==3:
            cls.form = Circle()
        elif val==4:
            cls.form = Triangle()
        # end of switch statement
        # then for each formation ask point B, ask 

    # end of askFormation
    @classmethod
    def handleNumDrones(cls):
        num = cls.form.setNumDrones()
        ans = cls.form.checkFormation(num)
        if ans == False:
            print "Sorry that combo is not possible. Enter 0 to renenter the num of drones or 1 to choose a different formation.. "
            choice = int(raw_input())
            if choice == 0:
                cls.handleNumDrones()
            elif choice == 1:
                cls.askFormation()
            else:
                cls.handleNumDrones()
        else:
            print "Good to Go!"

    # @classmethod
    # def setNumDrones(cls) {
    #        print "How many drones are there?";
    #        numDrones = int(raw_input())
    # form.setNumDrones
    #     }
    #     

if __name__ == '__main__':
    import sys
    Main.main(sys.argv)

