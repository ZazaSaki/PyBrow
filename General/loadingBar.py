import time
import sys
from typing import ValuesView

global x, max, title
max = 0
x = 0
title = "progress"
clean = "_______________________________________________________"
dynamicDisplay = {}


def show():
    sys.stdout.write("\r%s %i/%i" % (title, x, max))
    pass


def cleanDisplay():
    global clean
    sys.stdout.write(clean)
    pass


def openCounter(message, finish):
    global max, title, x
    max = finish
    title = message
    x = 0
    show()
    pass


def updateCounter(progress):
    global x
    x = progress
    show()
    pass


def closeCounter():
    global x
    sys.stdout.flush()
    print(" ")
    x = 0
    pass


# Dynamic Counter
def setDisplayInfo(name, val, max):
    global dynamicDisplay
    dynamicDisplay[name] = {"val": val, "max": max}
    complexUpdate(name, val)
    pass


def appendDisplayInfo(info):
    global dynamicDisplay
    dynamicDisplay.append(info)
    pass


def dynamicUpdate(name, info):
    global dynamicDisplay
    dynamicDisplay[name]["val"] = info


def getDynamicString():
    global dynamicDisplay
    output = "\r"
    for display in dynamicDisplay:
        message = display
        val = getFormatString(dynamicDisplay[message]["val"])
        max = getFormatString(dynamicDisplay[message]["max"])

        output += message + ": " + val + "/" + max + " ; "
    output += "             "
    return output


def getFormatString(val):
    return "{}".format(val)


def complexShow():
    sys.stdout.write(getDynamicString())


def complexUpdate(name, val):
    dynamicDisplay[name]["val"] = val
    complexShow()
    pass


def complexOpenCouter(name, val, max):
    setDisplayInfo(name, val, max)
    pass


def removeInfo(name):
    global dynamicDisplay

    del dynamicDisplay[name]
    # cleanDisplay()
    complexShow()
    pass


def test():
    openCounter("yea", 5)
    for i in range(5):
        updateCounter(i+1)
    closeCounter()
    pass
