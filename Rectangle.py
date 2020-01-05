#!/usr/bin/env python
""" generated source for module Rectangle """
# 
#  *  class Rectnagle, concetere extends Shape - write a description of the class here
#  *
#  * @author Jyoti Rani
#  * @version 0.1 11/07/19
#  
import java.util.Scanner

class Rectangle(Shape):
    """ generated source for class Rectangle """
    def printShriKishoriKishore(self):
        """ generated source for method printShriKishoriKishore """
        print "ShriKishoriKishore"

    def checkFormation(self, numDrones):
        """ generated source for method checkFormation """
        print "checking whether the chosen number of drones can be accomodated in the chosen formation..."
        formPoss = False
        if (numDrones % 4) == 0:
            formPoss = True
        return formPoss

