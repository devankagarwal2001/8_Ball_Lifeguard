# -*- coding: utf-8 -*-
"""
Created on Sun Jul 12 21:32:26 2015
@author: Stuart Grieve
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
import Indexer

def Test(img):
    
    #Now the table is cropped and warped, lets find the balls
    hsv = ToHSV(img)
    
    lower_color, upper_color = GetClothColor(hsv)    
    
    contours = GetContours(hsv, lower_color, upper_color,19)
        
    centers = FindTheBalls(img, contours)
    print(len(centers))
    FindTheColors(img,centers)

def LoadImage(filename):
    """
    Loads an image file
    """
    #img is loaded in bgr colorspace
    return cv2.imread(filename)

def ToHSV(img):
    """
    Convert an image from BGR to HSV colorspace
    """
    return cv2.cvtColor(img.copy(), cv2.COLOR_BGR2HSV)
    

def GetClothColor(hsv,search_width=45):
    """
    Find the most common HSV values in the image.
    In a well lit image, this will be the cloth
    """

    hist = cv2.calcHist([hsv], [0], None, [180], [0, 180])
    h_max = Indexer.get_index_of_max(hist)[0]
    
    hist = cv2.calcHist([hsv], [1], None, [256], [0, 256])
    s_max = Indexer.get_index_of_max(hist)[0]
    
    hist = cv2.calcHist([hsv], [2], None, [256], [0, 256])
    v_max = Indexer.get_index_of_max(hist)[0]

    # define range of blue color in HSV
    lower_color = np.array([h_max-search_width,s_max-search_width,v_max-search_width])
    upper_color = np.array([h_max+search_width,s_max+search_width,v_max+search_width])
    return lower_color, upper_color


def MaskTableBed(contours):
    """
    Mask out the table bed, assuming that it will be the biggest contour.
    """
            
    #The largest area should be the table bed    
    areas = []    
    for c in contours:
        areas.append(cv2.contourArea(c))
    
    #return the contour that delineates the table bed
    largest_contour = Indexer.get_index_of_max(areas)
    return contours[largest_contour[0]]

def distbetween(x1,y1,x2,y2):
    """
    Compute the distance between points (x1,y1) and (x2,y2)
    """

    return np.sqrt((x2-x1)*(x2-x1)+(y2-y1)*(y2-y1))

def Get_UL_Coord(contour,pad=10):
    """
    Get the upper left coordinate of the contour.
    """
    dists = []
    for c in contour:
        dists.append(distbetween(c[0][0],c[0][1],0,0))

    return (contour[Indexer.get_index_of_min(dists)[0]][0][0]-pad,contour[Indexer.get_index_of_min(dists)[0]][0][1]-pad)
    
def Get_UR_Coord(contour,imgXmax, pad=10):
    """
    Get the upper right coordinate of the contour.
    """
    dists = []
    for c in contour:
        dists.append(distbetween(c[0][0],c[0][1],imgXmax,0))

    return (contour[Indexer.get_index_of_min(dists)[0]][0][0]+pad,contour[Indexer.get_index_of_min(dists)[0]][0][1]-pad)

def Get_LL_Coord(contour,imgYmax, pad=10):
    """
    Get the lower left coordinate of the contour.
    """
    dists = []
    for c in contour:
        dists.append(distbetween(c[0][0],c[0][1],0,imgYmax))

    return (contour[Indexer.get_index_of_min(dists)[0]][0][0]-pad,contour[Indexer.get_index_of_min(dists)[0]][0][1]+pad)
    
def Get_LR_Coord(contour,imgXmax,imgYmax, pad=10):    
    """
    Get the lower right coordinate of the contour.
    """
    dists = []
    for c in contour:
        dists.append(distbetween(c[0][0],c[0][1],imgXmax,imgYmax))

    return (contour[Indexer.get_index_of_min(dists)[0]][0][0]+pad,contour[Indexer.get_index_of_min(dists)[0]][0][1]+pad)

def TransformToOverhead(img,contour):
    """
    Get the corner coordinates of the table bed by finding the minumum
    distance to the corners of the image for each point in the contour.
    
    Transform code is built upon code from: http://www.pyimagesearch.com/2014/05/05/building-pokedex-python-opencv-perspective-warping-step-5-6/ 
    """

    #get dimensions of image
    height, width, channels = img.shape 

    #find the 4 corners of the table bed
    UL = Get_UL_Coord(contour)
    UR = Get_UR_Coord(contour,width)  
    LL = Get_LL_Coord(contour,height)  
    LR = Get_LR_Coord(contour,width,height)  
    
    #store the coordinates in a numpy array    
    rect = np.zeros((4, 2), dtype = "float32")
    rect[0]= [UL[0],UL[1]]
    rect[1]= [UR[0],UR[1]]
    rect[2]= [LR[0],LR[1]]
    rect[3]= [LL[0],LL[1]]
    
    #get the width at the bottom and top of the image
    widthA = distbetween(LL[0],LL[1],LR[0],LR[1])
    widthB = distbetween(UL[0],UL[1],UR[0],UR[1])
    
    #choose the maximum width 
    maxWidth = max(int(widthA), int(widthB))
    maxHeight  = (maxWidth//2) #pool tables are twice as long as they are wide
    
    # construct our destination points which will be used to
    # map the image to a top-down, "birds eye" view
    dst = np.array([
    	[0, 0],
    	[maxWidth - 1, 0],
    	[maxWidth - 1, maxHeight - 1],
    	[0, maxHeight - 1]], dtype = "float32")
     
    # calculate the perspective transform matrix and warp
    # the perspective to grab the screen
    M = cv2.getPerspectiveTransform(rect, dst)
    warp = cv2.warpPerspective(img, M, (maxWidth, maxHeight))    


    plt.show()
    
    plt.show()
    return warp    

def GetContours(hsv, lower_color, upper_color,filter_radius):
    """
    Returns the contours generated from the given color range
    """
    cv2.imshow('hsv', hsv)
    # Threshold the HSV image to get only cloth colors
    mask = cv2.inRange(hsv, lower_color, upper_color)
    cv2.imshow('mask', mask)
    #use a median filter to get rid of speckle noise
    median = cv2.medianBlur(mask,filter_radius)
    cv2.imshow('median_detect', median)
    
    #get the contours of the filtered mask
    #this modifies median in place!
    contours, _ = cv2.findContours(median,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    return contours

def FindTheBalls(img, contours, similarity_threshold=20):
    """
    Find and circle all of the balls on the table.
    
    Currently struggles with balls on the rail. Not yet tested on clusters.
    """

    #compare the difference in area of a min bounding circle and the cotour area
    diffs = []
    indexes = []
    for i,contour in enumerate(contours):
        contourArea = cv2.contourArea(contour)
        (x,y),radius = cv2.minEnclosingCircle(contour)
        circleArea = 3.141 * (radius**2)
        diffs.append(abs(circleArea-contourArea))
        indexes.append(i)
        
    sorted_data = sorted(zip(diffs,indexes))
    
    diffs = [x[0] for x in sorted_data]
    
    #list of center coords as tuples
    centers = []    
    tmp_img = img.copy()
    for d,i in sorted_data:#zip(indexes,diffs):
        #if the contour is a similar shape to the circle it is likely to be a ball.
        if (d < diffs[0] * similarity_threshold):
            (x,y),radius = cv2.minEnclosingCircle(contours[i])
    
            cv2.circle(tmp_img,(int(x),int(y)),int(radius),(0,0,255),2)
            centers.append((int(y),int(x), int(radius)))
            print(int(y),int(x), int(radius))

    cv2.imshow('pool_ball_detect', tmp_img)
    #print(len(centers))
    return centers

def FindTheColors(img, centers):
    stripes = []
    solids = []
    cue = []
    eight_ball = []
    for (centerX,centerY,radius) in centers:
        print(centerX,centerY,radius)
        numOfWhitePixels = 0
        numOfBlackPixels = 0
        maxX, maxY, ___ = img.shape
        for x in range(centerX - radius, centerX + radius):
            for y in range(centerY - radius, centerY + radius):
                if (0 < x < maxX and 0 < y < maxY and img[x,y][0] > 200 and img[x,y][1] > 200 and img[x,y][2] > 200):
                    numOfWhitePixels +=1
                elif (0 < x < maxX and 0 < y < maxY and img[x,y][0] < 60 and img[x,y][1] < 60 and img[x,y][2] < 60):
                    numOfBlackPixels +=1
        print(numOfWhitePixels, numOfBlackPixels)
        if numOfBlackPixels > 10:
            eight_ball.append((centerX,centerY,radius))
            cv2.circle(img,(int(centerY),int(centerX)),int(radius),(0,0,0),2)
        elif numOfWhitePixels > 600:
            cue.append((centerX,centerY,radius))
            cv2.circle(img,(int(centerY),int(centerX)),int(radius),(255,255,255),2)
        elif numOfWhitePixels > 200:
            stripes.append((centerX,centerY,radius))
            cv2.circle(img,(int(centerY),int(centerX)),int(radius),(0,0,255),2)
        else:
            solids.append((centerX,centerY,radius))
            cv2.circle(img,(int(centerY),int(centerX)),int(radius),(0,255,0),2)
    cv2.imshow('colors_detected', img)

def mse(img1, img2):
   (h, w, x)= img1.shape
   diff = cv2.subtract(img1, img2)
   err = np.sum(diff**2)
   mse = err/(float(h*w))
   return mse

def show_img_compar(img_1, img_2 ):
    f, ax = plt.subplots(1, 2, figsize=(10,10))
    ax[0].imshow(img_1)
    ax[1].imshow(img_2)
    ax[0].axis('off') #hide the axis
    ax[1].axis('off')
    f.tight_layout()
    plt.show()

#(390,80) (1560,700)
imcap = cv2.VideoCapture(0) #1 or -1 once the camera is added I think
#imcap.set(3, 640) # set width as 640
#imcap.set(4, 480)
#img = LoadImage('img/test_2 copy.jpg')
#img = img[30:225,20:400]
#show_img_compar(img,cropped_img)

success,img = imcap.read()
img = img[80:680,390:1590]
plt.axis("off")
plt.imshow(img)

plt.show()

print(img.shape)

Test(img)
old_img = img
"""while True:
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break"""
    

while True:
    success,img = imcap.read()
    #img = LoadImage('img/test_2 copy.jpg')
    img = img[80:680,390:1590]
    
    cv2.imshow('orig_img', img)
    #if (mse(img,old_img) > 20):
    print(mse(img,old_img))
    Test(img)
    old_img = img
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break
#imcap.release()
cv2.destroyWindow('pool_ball_detect')
#img = LoadImage('img/pool_balls.jpeg')
#Test(img)
#img = LoadImage('img/pool_crop.png')
#Test(img)
#img = LoadImage('img/pool_crop_2.png') 
#Test(img)

""""
import cv2
import numpy as np

img = cv2.imread('img.png', cv2.IMREAD_GRAYSCALE)
n_white_pix = np.sum(img == 255)
print('Number of white pixels:', n_white_pix)
"""