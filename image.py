from PIL import Image
import numpy as np

def image():
    im  = Image.open("monalisa.jpg")
    row,col = im.size
    data = np.zeros([row,col])
    pixels = im.load
    pix = list(im.getdata())
    for i in range(row):
     	for j in range(col):
            #print pix[i*col +j]
		    data[i][j] = (pix[i*col + j])
    return None 

image()
