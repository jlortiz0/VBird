#!/usr/bin/python3

from Shape import Shape

class Rectangle(Shape):
    def __init__(self, numDrones, sideLen1, sideLen2):
        super().__init__(numDrones, sideLen1)
        self.sideLen2 = sideLen2

    def checkFormation(self):
        return not (self.numDrones % 4)

    def calcPoints(self, mastX, mastY, mastName):
        final = []
        perSide = self.numDrones//4
        for i in range(0, perSide):
            final.append((mastX+i*self.sideLen/perSide, mastY))
        for i in range(0, perSide):
            final.append((mastX+self.sideLen, mastY+i*self.sideLen2/perSide))
        for i in range(perSide, 0, -1):
            final.append((mastX+i*self.sideLen/perSide, mastY+self.sideLen2))
        for i in range(perSide, 0, -1):
            final.append((mastX, mastY+i*self.sideLen2/perSide))
        final[0] = mastName
        return final

class Square(Rectangle):
    def __init__(self, numDrones, sideLen):
        super().__init__(numDrones, sideLen, sideLen)
