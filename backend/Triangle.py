#!/usr/bin/python3

from Shape import Shape

class Triangle(Shape):
    # centroid 
    # enter the 3 angles, or 3 sides? 
    # classify as type of triangle and calculate median/alttud and stff
    # clac other drone pos
    # calc the linear direct path 2d
    # ask # of drones
    def printShriKishoriKishore(self):
        print("ShriKishoriKishore")

    def checkFormation(self, numDrones):
        print("checking whether the chosen number of drones can be accomodated in the chosen formation...")
        return not bool(numDrones % 3)

