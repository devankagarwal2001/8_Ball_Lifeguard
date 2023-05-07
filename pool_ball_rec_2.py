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
import pyfirmata
import serial

big_list = [[-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1],
            [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1], 
            [-1,-1], 
            [-1]]
prev_target = "hi"
BLUE = (255,0,0)        #BGR Color Representation of the Color Blue
GREEN = (0,255,0)       #BGR Color Representation of the Color Green
RED = (0,0,255) 
BLACK = (0,0,0)
WHITE = (255,255,255)
kernel = np.ones((3, 3), np.uint8)
X_MIN = 325
X_MAX = 1525
Y_MIN = 195
Y_MAX = 795
#img = img[30:645,305:1505]

def DetectPoolBalls():
    success,img = imcap.read()
    #img = LoadImage('img/pool_balls.jpeg')
    img = img[Y_MIN:Y_MAX,X_MIN:X_MAX]
    #success,img = imcap.read()
    cv2.imshow("preHough", img)
    circles, img = HoughCircleWrapper(img)
    cue, solids, eight_ball, stripes = FindTheColors(img,circles)
    final_list = BuildTheList(cue, solids, eight_ball, stripes)
    #print(final_list)
    final_list.append((X_MAX-X_MIN, Y_MAX-Y_MIN))
    return final_list

    #Now the table is cropped and warped, lets find the balls
    '''hsv = ToHSV(img)
    
    lower_color, upper_color = GetClothColor(hsv)    
    
    contours,contours2 = GetContours(hsv, lower_color, upper_color,21)
    centers = FindTheBalls(img, contours, RED, similarity_threshold=30)
    centers2 = FindTheBalls(img, contours2, GREEN, similarity_threshold=30)    
    #print(len(centers))
    #print(centers,centers2)
    centers = CombineTheList(centers,centers2)
    #IncreaseSaturation(img)
    cue, solids, eight_ball, stripes = FindTheColors(img,centers)
    final_list = BuildTheList(cue, solids, eight_ball, stripes)
    #print(final_list)
    final_list.append((X_MAX-X_MIN, Y_MAX-Y_MIN))
    return final_list'''
    
def IsPocket(ball,img):
     height, width, ____ = img.shape
     if (ball[0] +30 > width or ball[0] - 30 < 0) and ((ball[1] +30 > height or ball[1] - 30 < 0)):
         return True
     if (ball[0] < width/2 +30 or ball[0] > width/2-30) and ((ball[1] +30 > height or ball[1] - 30 < 0)):
         return True
     return False
    

def HoughCirclesTest(test):
    gray = cv2.cvtColor(test, cv2.COLOR_BGR2GRAY)
    img = cv2.medianBlur(gray,5)
    cv2.imshow ("gray", img)
    cimg = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    
    #test to find radius
    #circles = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, 1,5, param1 = 100, param2 = 30, minRadius = 0, maxRadius = 100)
    circles = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, .5,23, param1 = 40, param2 = 17, minRadius = 16, maxRadius = 25)
    if circles is not None:
        circles = np.uint16(np.around(circles))
    else:
        return None
    #for i in circles[0,:]:
        #if (not (int(i[0]) < 70 or int (i[1]) < 70)):
        #cv2.circle(test, (int(i[0]), int(i[1])), int(i[2]), (0, 255, 0), 2)
        #cv2.circle(test,  (int(i[0]), int(i[1])), 2, (0, 255, 0), 2)
    cv2.imshow("Circle Detection", test)
    return circles

def HoughCircleWrapper(img):
    circlesDetected = []
    for i in range(30):
        circles = HoughCirclesTest(img)
        if circles is not None:
            for ball in circles[0,:]:
                inList = False
                for ball2 in circlesDetected:
                    if CheckTwoEqualBalls(ball,ball2) or IsPocket(ball, img):
                        inList = True
                if not inList:
                    circlesDetected.append(ball)   
    return circlesDetected, img
    
def CombineTheList(centers, centers2):
    if len(centers) == 0:
        return centers2
    elif len(centers2) == 0:
        return centers
    newCenters = []
    for ball1 in centers:
        for ball2 in centers2:
            if CheckTwoEqualBalls(ball1, ball2):
                centers2.remove(ball2)
        newCenters.append(ball1)
    
    return newCenters + centers2
    
def CheckTwoEqualBalls(ball1, ball2):
    if abs(ball1[0] - ball2[0])>3 or abs(ball1[1] - ball2[1])>3:
        return False
    return True

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
    #cv2.imshow('median_detect', median)
    
    mask = cv2.erode(mask, kernel, iterations=3)
    mask = cv2.dilate(mask, kernel, iterations=11)
    
    mask = cv2.erode(mask, kernel, iterations=5)
    #mask = cv2.dilate(mask, kernel, iterations=10)
    #cv2.imshow('eroision&dilate', mask)
    
    #get the contours of the filtered mask
    #this modifies median in place!
    cv2.imwrite('inrangeandblur.jpeg',median)
    cv2.imwrite('erodeanddilate.jpeg',mask)
    contours, _ = cv2.findContours(median,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    contours2, _ = cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    return contours,contours2

def FindTheBalls(img, contours, color, similarity_threshold=15):
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
        #if radius > 15:
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
            if radius > 15: #and y <1130 and x <1130:
                cv2.circle(tmp_img,(int(x),int(y)),int(radius),color,2)
                centers.append((int(y),int(x), int(radius)))
    #cv2.imshow("test", tmp_img)
    return centers

def FindTheColors(img, centers):
    stripes = []
    solids = []
    cue = []
    eight_ball = []
    new_tmp_centers = []
    maxWhitePixels = -1
    for (centerY,centerX,radius) in centers:
        numOfWhitePixels = 0
        numOfBlackPixels = 0
        numOfOtherPixels = 0
        maxX, maxY, ___ = img.shape
        #print(centerY, centerX)
        if (centerY > 820 and centerY < 840):
            tmp_img = img[centerX - radius:centerX + radius,centerY - radius:centerY + radius]
            #cv2.imshow("tmp_img", tmp_img)
        for x in range(centerX - radius, centerX + radius):
            for y in range(centerY - radius, centerY + radius):
                """if (centerY > 655 and centerY < 675):
                    print(x,y)
                    print(img[x,y])"""
                if lengthOfLine(centerX,centerY,x,y) >radius:
                    continue
                if (0 < x < maxX and 0 < y < maxY and img[x,y][0] > 190 and img[x,y][1] > 190 and img[x,y][2] > 190):
                    numOfWhitePixels +=1
                elif (0 < x < maxX and 0 < y < maxY and img[x,y][0] < 90 and img[x,y][1] < 90 and img[x,y][2] < 90):
                    numOfBlackPixels +=1
                else:
                    numOfOtherPixels +=1
        #print(numOfBlackPixels, numOfWhitePixels, numOfOtherPixels)
        if numOfBlackPixels > 500:
            eight_ball.append((centerY,centerX,radius))
            cv2.circle(img,(int(centerY),int(centerX)),int(radius),BLACK,2)
        elif numOfWhitePixels > 500 and numOfWhitePixels > maxWhitePixels:
            cue.append((centerY,centerX,radius))
            cv2.circle(img,(int(centerY),int(centerX)),int(radius),WHITE,2)
            if maxWhitePixels == -1:
                maxWhitePixels = numOfWhitePixels
            else:
                cue.pop()
                tmp_x,tmp_y,tmp_rad = cue.pop()
                cue.append((centerY,centerX,radius))
                cv2.circle(img,(int(centerY),int(centerX)),int(radius),WHITE,2)
                cv2.circle(img,(int(tmp_x),int(tmp_y)),int(tmp_rad),RED,2)
                stripes.append((tmp_x,tmp_y,tmp_rad))
                maxWhitePixels = numOfWhitePixels
        elif numOfWhitePixels > 250:
            stripes.append((centerY,centerX,radius))
            cv2.circle(img,(int(centerY),int(centerX)),int(radius),RED,2)
        else:
            solids.append((centerY,centerX,radius))
            cv2.circle(img,(int(centerY),int(centerX)),int(radius),GREEN,2)
    #cv2.imshow('colors_detected', img)
    cv2.imwrite('colors.jpeg',img)
    solids.sort(key = compare)
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
        if (ball < 16):
            final_list[0][ball] = cue[ball][0]
            final_list[1][ball] = cue[ball][1]
    for ball in range(solids_size):
        if (ball + 1 < 16):
            final_list[0][ball+1] = solids[ball][0]
            final_list[1][ball+1] = solids[ball][1]
    for ball in range(eight_ball_size):
        if (ball+8 < 16):
            final_list[0][ball+8] = eight_ball[ball][0]
            final_list[1][ball+8] = eight_ball[ball][1]
    for ball in range(stripes_size):
        if (ball+9 < 16):
            final_list[0][ball+9] = stripes[ball][0]
            final_list[1][ball+9] = stripes[ball][1]
    return final_list
        
def lengthOfLine(x1,y1,x2,y2):
    return math.sqrt((x2-x1)**2 +(y2-y1)**2)       

def checkEquality(tempList, big_list):
    for i in range(2):
        for j in range(16):
            if abs(int(tempList[i][j]) - int(big_list[i][j]))>6:
                '''print("DIFFERENT ball")
                print(j)
                print(tempList[i][j] - big_list[i][j])
                print(abs(tempList[i][j] - big_list[i][j]))
                print(tempList[0][j])
                print(big_list[0][j])
                print(tempList[1][j])
                print(big_list[1][j])'''
                return False
    return True

def compare(ball):
  return ball[0]


#to call from Devanks Code
#call after
def detect_changes(tempList, target):

    global big_list
    global prev_target
    #(prev_target, target)
    stablize = False
    while(not stablize):
        time.sleep(.5)
        print("stabilizing")
        newList = DetectPoolBalls()
        newList.append(target)
        if(checkEquality(newList,big_list) and prev_target == target):
            stablize = True
        else:
            print(newList)
            print(big_list)
            big_list = newList
            prev_target = target
                
        #print(newList[3], target, prev_target, big_list[3])
    shot_calculation.start_calc(big_list[0],big_list[1],big_list[2],big_list[3])

arduino = serial.Serial(port = '/dev/cu.usbmodem141101',baudrate=115200, timeout=0)
imcap = cv2.VideoCapture(0) 
final_list = DetectPoolBalls()
final_list = DetectPoolBalls()
final_list = DetectPoolBalls()
final_list = DetectPoolBalls()
final_list = DetectPoolBalls()
while True:
    data = arduino.readline()
    #cv2.waitKey()
    if data:
        data = data.decode()
        data = data.encode()
        if data == b'1':
            print ("Jimmy")
            final_list = DetectPoolBalls()
            #print(final_list)
            final_list.append("Stripe")
            detect_changes(final_list, "Stripe")
            print("Stripes done")
            #call Devank's function with my code
        elif data ==  b'0':
            print ("Devank")
            final_list = DetectPoolBalls()
            #print(final_list)
            final_list.append("Solid")
            detect_changes(final_list,"Solid")
            print("Solids done")
            #call Devank's function with my code
        elif data != "b''":
            print ("You Entered :", data)
    #break
#imcap.release()
cv2.destroyWindow('pool_ball_detect')