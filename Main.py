#!/usr/bin/env python
""" generated source for module Main """
# 
#  *  class Main - 
#  *
#  * @author Jyoti Rani
#  * @version 0.1 11/07/19
#  
import java.util.Scanner

class Main(object):
    """ generated source for class Main """
    s = Scanner(System.in_)
    form = Shape()

    # public static int numDrones = 0;
    @classmethod
    def main(cls, args):
        """ generated source for method main """
        print Math.atan((4 / 3))
        askFormation()
        handleNumDrones()
        # get Master Drone's A Point Position MAPos[]
        MAPos = cls.form.getCurrPosMasterA()
        cls.form.setCurrPosMasterA(MAPos)
        cls.form.printCurrPosMasterA(MAPos)
        # get Master Drone's B Point Position MAPos[]
        MPOSB = cls.form.askFinalDest()
        cls.form.setDirectDistM()
        dist = cls.form.getDirectDistM()
        print "The direct distance to Point B is: " + dist + " meters"
        print "What is the desired velocity in (m/s, of the swarm. Enter 0 to skip vel question and enter the time in seconds instead: ")
        vel = cls.s.nextDouble()
        if vel == 0:
            print "What is the desired duration of flight in seconds?",
            # update teh GUI with the time value
            print "The calculated velocity is: " + calcVel + " m/s",
        else:
            print "The calculated time is: " + calcTime + "seconds"
        print cls.form.calcDirection()
        cls.form.printShriKishoriKishore()

    #  end of main method
    @classmethod
    def askFormation(cls):
        """ generated source for method askFormation """
        print "\nSquare\t1\nRectangle\t2\nCircle\t3\nTriangle\t4\nHexagon\t5\n\nEnter the number corresponding to the formation you want to choose: "
        val = cls.s.nextInt()
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
        """ generated source for method handleNumDrones """
        num = cls.form.setNumDrones()
        ans = cls.form.checkFormation(num)
        if ans == False:
            print "Sorry that combo is not possible. Enter 0 to renenter the num of drones or 1 to choose a different formation.. "
            if choice == 0:
                cls.handleNumDrones()
            elif choice == 1:
                cls.askFormation()
            else:
                cls.handleNumDrones()
        else:
            print "Good to Go!"

    # public static void setNumDrones(){
    #        print "How many drones are there?";
    #        int numDrones = s.nextInt();
    # form.setNumDrones
    #     }
    #     


if __name__ == '__main__':
    import sys
    Main.main(sys.argv)

