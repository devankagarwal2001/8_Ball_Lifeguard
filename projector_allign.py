import math
from array import *
import cv2 as cv
import numpy as np
import pyfirmata
import time
import serial
from PIL import Image

BLUE = (255,0,0)        #BGR Color Representation of the Color Blue
GREEN = (0,255,0)       #BGR Color Representation of the Color Green
RED = (0,0,255)         #BGR Color Representation of the Color Red
WHITE = (255,255,255)   #BGR Color Representation of the Color White
YELLOW = (0,255,255)    #BGR Color Representation of the Color Yellow
GREY = (150,150,150)    #BGR Color Representation of the Color Grey
RADIUS_POCKET = 30  

pockets = [[0,30],[700,30],[1400,30],[1400,740],[700,740],[0,740]]
img = np.zeros((800,1400,3), np.uint8)
cv.rectangle (img,pockets[0],pockets[3],WHITE,-1)
for pocket in pockets:
        cv.circle(img,(pocket[0],pocket[1]),RADIUS_POCKET,RED,-1)  
for i in range (100,701,30):
    cv.line(img,(100,i),(1300,i),BLUE,2)
for i in range (100,1301,30):
    cv.line(img,(i,100),(i,700),BLUE,2)
cv.imwrite('allign.jpeg',img)
im = Image.open("allign.jpeg")
rotated_image1 = im.rotate(60)
im_rotate = im.rotate(2)
im_rotate.show()
