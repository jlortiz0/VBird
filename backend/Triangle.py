#!/usr/bin/python3

import math
from Shape import Shape

class Triangle(Shape):
    def checkFormation(self, numDrones):
        return not (numDrones % 3)

    def calcPoints(self, mastX, mastY, mastName):
        final = []
        perSide = self.numDrones//3
        sin = math.sqrt(3)/2
        for i in range(0, self.sideLen, self.sideLen//perSide):
            final.append((mastX+i/2, mastY+i*sin))
        topH = self.sideLen*sin
        for i in range(0, self.sideLen, self.sideLen//perSide):
            final.append((mastX+(i+self.sideLen)/2, mastY+topH-i*sin))
        for i in range(self.sideLen, 0, -self.sideLen//perSide):
            final.append((mastX+i, mastY))
        final[0] = mastName
        return final
    

