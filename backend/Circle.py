#!/usr/bin/python3

import math
from Shape import Shape
from Triangle import Triangle
from Rectangle import Square

class Circle(Shape):
    def __init__(self, numDrones, sideLen):
        super().__init__(numDrones, sideLen)
        if not (numDrones % 4):
            # Safe? Sort of. Works? Yes.
            self.__class__ = Square
            self.sideLen2 = sideLen
        elif not (numDrones % 3):
            self.__class__ = Triangle

    def checkFormation(self):
        return True

    def calcPoints(self, mastX, mastY, mastName):
        if self.numDrones == 1:
            return (mastName,)
        elif self.numDrones == 2:
            return (mastName, (mastX, mastY+self.sideLen*2))
        radBetw = math.tau/self.numDrones
        final = [mastName]
        mastX -= 1
        for x in range(1, self.numDrones):
            i = x*radBetw
            final.append((math.sin(i)*self.sideLen+mastX, math.cos(i)*self.sideLen+mastY))
        return final
