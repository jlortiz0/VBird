#!/usr/bin/env python
""" generated source for module Triangle """
class Triangle(Shape):
    """ generated source for class Triangle """
    # centroid 
    # enter the 3 angles, or 3 sides? 
    # classify as type of triangle and calculate median/alttud and stff
    # clac other drone pos
    # calc the linear direct path 2d
    # ask # of drones
    def printShriKishoriKishore(self):
        """ generated source for method printShriKishoriKishore """
        print "ShriKishoriKishore"

    def checkFormation(self, numDrones):
        """ generated source for method checkFormation """
        print "checking whether the chosen number of drones can be accomodated in the chosen formation..."
        formPoss = False
        if (numDrones % 3) == 0:
            formPoss = True
        return formPoss

