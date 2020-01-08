#!/usr/bin/python3

from Shape import Shape

class Rectangle(Shape):
    def printShriKishoriKishore(self):
        print("ShriKishoriKishore")

    def checkFormation(self, numDrones):
        print("checking whether the chosen number of drones can be accomodated in the chosen formation...")
        return not bool(numDrones % 4)

