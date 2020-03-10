#!/usr/bin/python3

class Shape(object):
    def __init__(self, numDrones, sideLen):
        if numDrones < 1:
            raise ValueError("numDrones requires positive integer")
        if sideLen < 1:
            raise ValueError("sideLen requires positive integer")
        self.numDrones = numDrones
        self.sideLen = sideLen

    def checkFormation(self):
        raise NotImplementedError

    def calcPoints(self):
        raise NotImplementedError
