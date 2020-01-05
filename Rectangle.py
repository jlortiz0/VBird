#!/usr/bin/env python

from Shape import Shape

class Rectangle(Shape):
    def printShriKishoriKishore(self):
        print "ShriKishoriKishore"

    def checkFormation(self, numDrones):
        print "checking whether the chosen number of drones can be accomodated in the chosen formation..."
        formPoss = False
        if (numDrone % 4) == 0:
            formPoss = True
        return formPoss

