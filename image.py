from PIL import Image
import numpy as np

def image():
    im  = Image.open("monalisa.jpg")
    row,col = im.size
    data = np.zeros([row,col])
    pixels = im.load
    for i in range(row):
    	for j in range(col):
    		print pixels[i,j]
		    #data[i,j] = pixels[i,j]
    return None 

image()
