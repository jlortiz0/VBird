#!/usr/bin/python3

import math
from Shape import Shape, Circle
from Rectangle import Rectangle
from Square import Square
from Triangle import Triangle

class Main(object):
    form = Shape()

    # public static int numDrones = 0;
    @classmethod
    def main(cls, args):
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
        print("The direct distance to Point B is: " + str(dist) + " meters")
        vel = float(input("What is the desired velocity in m/s, of the swarm. Enter 0 to skip vel question and enter the time in seconds instead: "))
        if vel == 0:
            time = float(input("What is the desired duration of flight in seconds? "))
            # update teh GUI with the time value
            calcVel = cls.form.getVelocity(time)
            print("The calculated velocity is: " + str(calcVel) + " m/s", end=' ')
        else:
            calcTime = cls.form.getTime(vel)
            print("The calculated time is: " + str(calcTime) + "seconds")
        print(cls.form.calcDirection())
        cls.form.printShriKishoriKishore()

    #  end of main method
    @classmethod
    def askFormation(cls):
        print("\n1. Square\n2. Rectangle\n3. Circle\n4. Triangle\n5. Hexagon\n")
        val = int(input("Enter the number corresponding to the formation you want to choose: "))
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
            print("Sorry that combo is not possible. Enter 0 to renenter the num of drones or 1 to choose a different formation.. ")
            choice = int(input())
            if choice == 0:
                cls.handleNumDrones()
            elif choice == 1:
                cls.askFormation()
            else:
                cls.handleNumDrones()
        else:
            print("Good to Go!")

if __name__ == '__main__':
    import sys
    Main.main(sys.argv)

