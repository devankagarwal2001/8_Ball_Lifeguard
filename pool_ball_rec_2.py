# -*- coding: utf-8 -*-
"""
Created on Sun Jul 12 21:32:26 2015
@author: Stuart Grieve
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
import Indexer
import time
import shot_calculation
import math

big_list = [[-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1],
            [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1]]
BLUE = (255,0,0)        #BGR Color Representation of the Color Blue
GREEN = (0,255,0)       #BGR Color Representation of the Color Green
RED = (0,0,255) 
kernel = np.ones((3, 3), np.uint8)


def DetectPoolBalls():
    success,img = imcap.read()
    #img = LoadImage('img/pool_balls.jpeg')
    img = img[100:700,360:1520]
    #Now the table is cropped and warped, lets find the balls
    hsv = ToHSV(img)
    
    lower_color, upper_color = GetClothColor(hsv)    
    
    contours = GetContours(hsv, lower_color, upper_color,21)
        
    centers = FindTheBalls(img, contours, similarity_threshold=18)
    #print(len(centers))
    cue, solids, eight_ball, stripes = FindTheColors(img,centers)
    final_list = BuildTheList(cue, solids, eight_ball, stripes)
    print(final_list)
    return final_list

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

def GetContours(hsv, lower_color, upper_color,filter_radius):
    """
    Returns the contours generated from the given color range
    """
    # Threshold the HSV image to get only cloth colors
    mask = cv2.inRange(hsv, lower_color, upper_color)
    #use a median filter to get rid of speckle noise
    median = cv2.medianBlur(mask,filter_radius)
    cv2.imshow('median_detect', median)
    mask = cv2.erode(mask, kernel, iterations=6)
    mask = cv2.dilate(mask, kernel, iterations=3)
    
    #get the contours of the filtered mask
    #this modifies median in place!
    contours, _ = cv2.findContours(median,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    return contours

def FindTheBalls(img, contours, similarity_threshold=15):
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
            if radius > 15 and y <1130 and x <1130:
                cv2.circle(tmp_img,(int(x),int(y)),int(radius),(0,0,255),2)
                centers.append((int(y),int(x), int(radius)))

    return centers

def FindTheColors(img, centers):
    stripes = []
    solids = []
    cue = []
    eight_ball = []
    new_tmp_centers = []
    maxWhitePixels = -1
    for (centerX,centerY,radius) in centers:
        numOfWhitePixels = 0
        numOfBlackPixels = 0
        numOfOtherPixels = 0
        maxX, maxY, ___ = img.shape
            
        for x in range(centerX - radius, centerX + radius):
            for y in range(centerY - radius, centerY + radius):
                if lengthOfLine(centerX,centerY,x,y) >radius:
                    continue
                if (0 < x < maxX and 0 < y < maxY and img[x,y][0] > 180 and img[x,y][1] > 180 and img[x,y][2] > 180):
                    numOfWhitePixels +=1
                elif (0 < x < maxX and 0 < y < maxY and img[x,y][0] < 60 and img[x,y][1] < 60 and img[x,y][2] < 60):
                    numOfBlackPixels +=1
                else:
                    numOfOtherPixels +=1
        
        if numOfBlackPixels > 100:
            eight_ball.append((centerY,centerX,radius))
            cv2.circle(img,(int(centerY),int(centerX)),int(radius),(0,0,0),2)
        elif numOfWhitePixels > 500 and numOfWhitePixels > maxWhitePixels:
            cue.append((centerY,centerX,radius))
            cv2.circle(img,(int(centerY),int(centerX)),int(radius),(255,255,255),2)
            if maxWhitePixels == -1:
                maxWhitePixels = numOfWhitePixels
            else:
                tmp_x,tmp_y,tmp_rad = cue.pop()
                cue.append((centerY,centerX,radius))
                cv2.circle(img,(int(centerY),int(centerX)),int(radius),(255,255,255),2)
                cv2.circle(img,(int(tmp_y),int(tmp_x)),int(tmp_rad),RED,2)
                stripes.append((tmp_y,tmp_x,tmp_rad))
                maxWhitePixels = numOfWhitePixels
        elif numOfWhitePixels > 150:
            stripes.append((centerY,centerX,radius))
            cv2.circle(img,(int(centerY),int(centerX)),int(radius),RED,2)
        else:
            solids.append((centerY,centerX,radius))
            cv2.circle(img,(int(centerY),int(centerX)),int(radius),GREEN,2)
    cv2.imshow('colors_detected', img)
    cue.sort(key = compare)
    solids.sort(key = compare)
    """eight_ball = eight_ball.sort()"""
    stripes.sort(key = compare)
    return cue, solids, eight_ball, stripes

def BuildTheList(cue, solids, eight_ball, stripes):
    cue_size = len(cue)
    solids_size = len(solids)
    eight_ball_size = len(eight_ball)
    stripes_size = len(stripes)
    final_list = [[-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1],
                  [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1]]
    for ball in range(cue_size):
        final_list[0][ball] = cue[ball][0]
        final_list[1][ball] = cue[ball][1]
    for ball in range(solids_size):
        final_list[0][ball+1] = solids[ball][0]
        final_list[1][ball+1] = solids[ball][1]
    for ball in range(eight_ball_size):
        final_list[0][ball+8] = eight_ball[ball][0]
        final_list[1][ball+8] = eight_ball[ball][1]
    for ball in range(stripes_size):
        final_list[0][ball+9] = stripes[ball][0]
        final_list[1][ball+9] = stripes[ball][1]
    return final_list
        
def lengthOfLine(x1,y1,x2,y2):
    return math.sqrt((x2-x1)**2 +(y2-y1)**2)       

def checkEquality(tempList, big_list):
    for i in range(2):
        for j in range(16):
            if abs(tempList[i][j] - big_list[i][j])>3:
                print("DIFFERENT ball")
                print(tempList[i][j])
                return False
    return True

def compare(ball):
  return ball[0]


#to call from Devanks Code
#call after
def detect_changes(tempList):

    global big_list
    if (checkEquality(tempList,big_list)):
        return
    else:
        stablize = False
        while(not stablize):
            time.sleep(.5)
            print("stabilizing")
            newList = DetectPoolBalls()
            if(checkEquality(newList,big_list)):
                stablize = True
            else:
                big_list = newList
        shot_calculation.start_calc(big_list[0],big_list[1])

imcap = cv2.VideoCapture(0) 
final_list = DetectPoolBalls()
final_list = DetectPoolBalls()
final_list = DetectPoolBalls()
final_list = DetectPoolBalls()
final_list = DetectPoolBalls()
while True:
    final_list = DetectPoolBalls()
    #print(final_list)
    #detect_changes(final_list)
    #call Devank's function with my code
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break
    #break
#imcap.release()
cv2.destroyWindow('pool_ball_detect')
