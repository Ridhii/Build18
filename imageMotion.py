from PIL import Image
import numpy as np
import os, sys, inspect, thread, time, math

import Leap
from Leap import CircleGesture, KeyTapGesture, ScreenTapGesture, SwipeGesture

# Assuming we get an image of size 64X64


sList = [3, 2, 1, 0, 7, 6, 5, 4, 11, 10, 9, 8, 15, 14, 13 ,12]


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

    row = numRows - int((y - screenYoffset)/tileHeight) -1
    col = int((x - screenXoffset)/tileWidth) 

    print row, col

    return None

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
    scIm = scrambleImage(tileList,im,sList)
    scIm.show()
    hgIm = highlightOnSelect(1,2,scIm)
    hgIm.show()
    return None

def putBorders(im):
    width,height = im.size   
    inc = height/4
    # putting borders vertically
    startX = width/4
    while(startX < width):
        for y in xrange(height):
            im.putpixel((startX,y),(0,0,0))
        startX += inc
    # putting borders horizontally
    startY = height/4
    while(startY < height):
        for x in xrange(width):
            im.putpixel((x,startY),(0,0,0))
        startY += inc
    return im
    
def blacken15(im):
    width,height = im.size
    # square images only
    inc = height/4
    x0 = width - inc
    y0 = height - inc
    x1 = width
    y1 = height
    tile15 = (x0,y0,x1,y1)
    region = im.crop(tile15)
    row,col = region.size
    for i in range (row):
        for j in range(col):
            region.putpixel((i,j), (0,0,0))
    im.paste(region,tile15)
    return im

def getTileList(im):
    x0 = 0
    y0 = 0
    width,height = im.size
    inc = height/4
    tileList = [ 0 for i in range(16)]
    i = 0
    # go vertically
    while(y0 < height):
        # go horizontally
        while( x0 < width):
            x1 = x0 + inc
            y1 = y0 + inc
            tile = im.crop((x0,y0,x1,y1))
            tileList[i] = tile
            i += 1
            x0 += inc
        x0 = 0
        y0 += inc
    return tileList

def scrambleImage(tileList,im,scList):
    
    # tileList = a list representing the current
    # tiles in form of a list. Each tile is a 
    # sub-image of 16X16
    # scList is the list of indices reprsenting the 
    # order of tiles to appear in the scrambled image
    width,height = im.size
    x0 = 0
    y0 = 0
    inc = height/4
    # pasting on an empty image
    im = Image.new('RGB', (width,height))
    # pasting tiles row-wise
    for i in range(len(scList)):
        # getting the index
        index = scList[i]
        # getting the tile to paste
        tile = tileList[index]
        if(x0 == 3*inc):
            x1 = x0 + inc
            y1 = y0 + inc
            box = (x0,y0,x1,y1)
            im.paste(tile,box)
            x0 = 0
            y0 += inc
        else:
            x1 = x0 + inc
            y1 = y0 + inc
            box = (x0,y0,x1,y1)
            im.paste(tile,box)
            x0 += inc
    return im

def highlightOnSelect(tileX,tileY,im):
    width,height = im.size
    inc = height/4
    startX = tileX * inc  #(I)
    startY  = tileY * inc  #(2I)
    endX = startX + inc
    endY = startY + inc
    
    # highlight both vertical
    # sides of the tile
    while(startX < endX):
        for y in xrange(inc):
            im.putpixel((startX,startY + y),(255,255,255))
        startX += inc - 1
    
    # highlight both horizontal 
    # sides of the tile
    startX = tileX * inc
    while(startY < endY):
        for x in xrange(inc):
            im.putpixel((startX + x, startY), (255,255,255))
        startY += inc - 1
        
    return im




  




image()
main()
