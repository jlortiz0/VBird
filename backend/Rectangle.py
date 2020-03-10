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
        for i in range(0, self.sideLen, self.sideLen//perSide):
            final.append((mastX+i, mastY))
        for i in range(0, self.sideLen2, self.sideLen2//perSide):
            final.append((mastX+self.sideLen, mastY+i))
        for i in range(self.sideLen, 0, -self.sideLen//perSide):
            final.append((mastX+i, mastY+self.sideLen2))
        for i in range(self.sideLen2, 0, -self.sideLen2//perSide):
            final.append((mastX, mastY+i))
        final[0] = mastName
        return final

class Square(Rectangle):
    def __init__(self, numDrones, sideLen):
        super().__init__(numDrones, sideLen, sideLen)
