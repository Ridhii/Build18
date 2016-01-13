from PIL import Image
import numpy as np

# Assuming we get an image of size 64X64

upper15 = 48
left15  = 48
bottom15 = 64
right15  = 64

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







image()
