#!/usr/bin/python3

from Shape import Shape

class Square(Shape):
    # centroid 
    # constant distances for square/rect 
    # clac other drone pos
    # calc the linear direct path 2d
    # ask # of drones
    def printShriKishoriKishore(self):
        print("ShriKishoriKishore")

    def checkFormation(self, numDrones):
        print("checking whether the chosen number of drones can be accomodated in the chosen formation...")
        return not bool(numDrones % 4)

