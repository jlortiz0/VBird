#!/usr/bin/env python

from Shape import Shape

class Square(Shape):
    # centroid 
    # constant distances for square/rect 
    # clac other drone pos
    # calc the linear direct path 2d
    # ask # of drones
    def printShriKishoriKishore(self):
        print "ShriKishoriKishore Enter name"
        s = raw_input()

    def checkFormation(self, numDrones):
        print "checking whether the chosen number of drones can be accomodated in the chosen formation..."
        formPoss = False
        if (numDrones % 4) == 0:
            formPoss = True
        return formPoss

