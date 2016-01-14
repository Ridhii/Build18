from PIL import Image
import numpy as np
import os, sys, inspect, thread, time, math

import Leap
from Leap import CircleGesture, KeyTapGesture, ScreenTapGesture, SwipeGesture

# Assuming we get an image of size 64X64

upper15 = 48
left15  = 48
bottom15 = 64
right15  = 64


def main():
    controller = Leap.Controller()
    while(not(controller.is_connected)): continue
    print "connected"
    enable_swipe(controller)
    enable_screentap(controller)
    lastFrameID = -1
    previousTapID = -1
    previousTapreached = False
    while(True):
        # frame = controller.frame()
        # if(frame.is_valid):
        #     print frame.id
        #     for gesture in frame.gestures():
        #         if(gesture.type is Leap.Gesture.TYPE_SWIPE):
        #             swipe = Leap.SwipeGesture(gesture)
        #             print "                    SWIPE "

        thisFrame = controller.frame()
        
        maxHistory = 60

        for i in range (maxHistory):
            frame = controller.frame(i)

            if (frame.id == lastFrameID): break
            if (not frame.is_valid): break
            if (frame.is_valid):
                for gesture in frame.gestures():
                    # if((i== 0) and (gesture.type is Leap.Gesture.TYPE_SWIPE)):
                    #     swipe = Leap.SwipeGesture(gesture)
                    #     print "                    SWIPE "
                    if(gesture.is_valid and (gesture.type is Leap.Gesture.TYPE_SCREEN_TAP)):
                        if (gesture.id != previousTapID):
                            screenTap = Leap.ScreenTapGesture(gesture)
                            previousTapID = gesture.id
                            print "SCREEN_TAP"
                            selectTile(screenTap)
                        else:
                            previousTapreached = True
                if (previousTapreached): break

            lastFrameID = thisFrame.id

            

    return None

def selectTile(screenTap):
    screenWidth = 35.5 * 10
    screenHeight = 27 * 10
    numRows = 3
    numCols = 4

    tileWidth = screenWidth/numCols
    tileHeight = screenHeight/numRows

    screenYoffset = 0
    screenXoffset = - (17.75 * 10)

    x = screenTap.position.x
    y = screenTap.position.y

    tileY = numRows - int((y - screenYoffset)/tileHeight) -1
    tileX = int((x - screenXoffset)/tileWidth) 

    return (tileX, tileY)

def isValid(blankInd, (tileX, tileY)):

    if (tileX < 0) || (tileX > 3) || (tileY < 0) || (tileY > 3)):
        return False

    blankX = blankInd % 4
    blankY = int(blankInd / 4)

    correctCol = (tileX == blankX)
    correctRow = (tileY == blankY)

    isBlankTile = correctCol && correctRow
    
    return ((not isBlankTile) && (correctRow || correctCol))

def Move(blankInd, (tileX, tileY), currentState):
    blankX = blankInd % 4
    blankY = int(blankInd / 4)

    if(tileX == blankX): # move vertical
        moveby = abs(blankY - tileY)
        moveup = tileY > blankY
        if (moveup): # move tile u[]
            moveIndex = blankIndex + 4
            for i in range(moveby):
                movedTile = currentState[moveIndex]
                blank = currentState[blankInd]
                currentState[moveIndex] = blank
                currentState[blankInd] = movedTile
                moveIndex += 4
                blankInd += 4

        else : #move tile down
            moveIndex = blankIndex - 4
            for i in range(moveby):
                movedTile = currentState[moveIndex]
                blank = currentState[blankInd]
                currentState[moveIndex] = blank
                currentState[blankInd] = movedTile
                moveIndex -= 4
                blankInd -= 4


    else if (tileY == blankY): # move horizontal
        moveby = abs(blankX - tileX)
        moveleft = tileX > blankX
        if (moveleft): # move tileleft
            moveIndex = blankIndex + 1
            for i in range(moveby):
                movedTile = currentState[moveIndex]
                blank = currentState[blankInd]
                currentState[moveIndex] = blank
                currentState[blankInd] = movedTile
                moveIndex += 1
                blankInd += 1

        else : # move tile Right
            moveIndex = blankIndex - 1
            for i in range(moveby):
                movedTile = currentState[moveIndex]
                blank = currentState[blankInd]
                currentState[moveIndex] = blank
                currentState[blankInd] = movedTile
                moveIndex -= 1
                blankInd -= 1

    ######### UPDATE BLANK INDEX GLOBAL OR PASS AROUND
    ## Both currentState and blankIndex have changed so pass them back 
    return (currentState, blankIndex)


def enable_swipe(controller):
    print "on_connect"
    controller.enable_gesture(Leap.Gesture.TYPE_SWIPE)
    controller.config.set("Gesture.Swipe.MinLength", 100.0)
    controller.config.set("Gesture.Swipe,MinVelocity", 400)
    controller.config.save()

def enable_screentap(controller):
    print "enabling_tap"
    controller.enable_gesture(Leap.Gesture.TYPE_SCREEN_TAP)
    controller.config.set("Gesture.ScreenTap.MinForwardVelocity", 15.0)
    controller.config.set("Gesture.ScreenTap.HistorySeconds", 0.5)
    controller.config.set("Gesture.ScreenTap.MinDistance", 0.5)
    controller.config.save()

def image():
    im  = Image.open("Image_2.jpg")
    row,col = im.size   # row = x, col = y
    data = [ ([0] * col) for row in xrange(row)]
    pixels = im.load
    pix = list(im.getdata())
    for i in range(row):
     	for j in range(col):
		    data[i][j] = (pix[i*col + j])

    newIm = putBorders(blacken15(im))
    newIm.show()
    tileList = getTileList(newIm)
    scrambleImage(tileList,im)
    return None

def putBorders(im):
    row,col = im.size   
    height = col
    width  = row
    # height = width
    increment = height/4
    startVal = width/4
    while(startVal < width):
        for i in range(height):
            im.putpixel((startVal,i), (0,0,0))
        startVal += increment
    startVal = height/4
    while(startVal < height):
        for i in range(height):
            im.putpixel((i,startVal), (0,0,0))
        startVal += increment
    tileList = getTileList(im)
    return im
    
def blacken15(im):
    tile15 = (upper15,left15,bottom15,right15)
    region = im.crop(tile15)
    row,col = region.size
    for i in range (row):
        for j in range(col):
            region.putpixel((i,j), (0,0,0))
    im.paste(region,tile15)
    return im

def getTileList(im):
    upper = 0
    left  = 0
    height,width = im.size
    inc = height/4
    tileList = [ 0 for i in range(16)]
    i = 0
    while(left < height):
        while(upper < width):
            bottom = upper + inc
            right  = left + inc
            tile = im.crop((upper,left,bottom,right))
            tileList[i] = tile
            i += 1
            upper += inc
        upper = 0
        left += inc
    return tileList

def scrambleImage(tileList,im):
    scList = [3, 2, 1, 0, 7, 6, 5, 4, 11, 10, 9, 8, 15, 14, 13 ,12]
    row,col = im.size
    upper = 0
    left = 0
    inc = row/4
    im = Image.new('RGB', (row,col))
    for i in range(len(scList)):
        index = scList[i]
        tile = tileList[index]
        if(upper == 3*inc):
            bottom = upper + inc
            right = left + inc
            box = (upper,left,bottom,right)
            upper += inc
            im.paste(tile,box)
            upper = 0
            left += inc
            
        else:
            bottom = upper + inc
            right = left + inc
            box = (upper,left,bottom,right)
            upper += inc
            im.paste(tile,box)

    im.show()








#image()
main()
