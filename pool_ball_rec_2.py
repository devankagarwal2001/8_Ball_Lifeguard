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
RED = (0,0,255)         #BGR Color Representation of the Color Red
BLACK = (0,0,0)         #BGR Color Representation of the Color Black
WHITE = (255,255,255)   #BGR Color Representation of the Color White
kernel = np.ones((3, 3), np.uint8)
X_MIN = 325
X_MAX = 1525
Y_MIN = 195
Y_MAX = 795

#This function will take an image of the pool table using the camera and crop
#the image so that only the pool table is in the image(currently the cropping
# is hard coded. Use align_camera.py to figure out the dimensions necessary). 
# It will call the hough circle function on the image and then color detection. 
# Finally it will build the list that shot calculation is expecting and return 
# it. 
def DetectPoolBalls():
    success,img = imcap.read()
    img = img[Y_MIN:Y_MAX,X_MIN:X_MAX]
    cv2.imshow("preHough", img)
    circles, img = HoughCircleWrapper(img)
    cue, solids, eight_ball, stripes = FindTheColors(img,circles)
    final_list = BuildTheList(cue, solids, eight_ball, stripes)
    final_list.append((X_MAX-X_MIN, Y_MAX-Y_MIN))
    return final_list
    
#This will detect if the pool ball is a pocket based on the position of the pool
#ball. It currently does not return true on the middle pockets.
def IsPocket(ball,img):
     height, width, ____ = img.shape
     if (ball[0] +30 > width or ball[0] - 30 < 0) and ((ball[1] +30 > height or ball[1] - 30 < 0)):
         return True
     if (ball[0] < width/2 +30 or ball[0] > width/2-30) and ((ball[1] +30 > height or ball[1] - 30 < 0)):
         return True
     return False
    
#This function will run HoughCircles on the image of the pool table and return 
#the circle that is found.
def HoughCirclesTest(test):
    gray = cv2.cvtColor(test, cv2.COLOR_BGR2GRAY)
    img = cv2.medianBlur(gray,5)
    cv2.imshow ("gray", img)
    cimg = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    
    circles = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, .5,23, param1 = 40, param2 = 17, minRadius = 16, maxRadius = 25)
    if circles is not None:
        circles = np.uint16(np.around(circles))
    else:
        return None
    cv2.imshow("Circle Detection", test)
    return circles

#This function will run the Hough Circle detection 30 times combining the list 
# each time removing if a ball is already in the list or if it is a pocket. This 
# is done to ensure that all of the balls are detected. Still struggled to detect
# some of the pool balls that were similar color to the pool table.
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
    return cv2.imread(filename)

#Convert an image from BGR to HSV colorspace
def ToHSV(img):    
    return cv2.cvtColor(img.copy(), cv2.COLOR_BGR2HSV)
    
#This function will loop through all of the centers of the balls on the table and
#look at the value of all the pixels. Then based on the number of white and black
#pixels it will detect classify whether each ball is a solid, stripe, the cue ball
#or the eight ball.
def FindTheColors(img, centers):
    stripes = []
    solids = []
    cue = []
    eight_ball = []
    new_tmp_centers = []
    maxWhitePixels = -1
    #loop through all of the balls
    for (centerY,centerX,radius) in centers:
        numOfWhitePixels = 0
        numOfBlackPixels = 0
        numOfOtherPixels = 0
        maxX, maxY, ___ = img.shape
        for x in range(centerX - radius, centerX + radius):
            for y in range(centerY - radius, centerY + radius):
                #For all pixels in the ball, detect whether it is white black or some other color
                if lengthOfLine(centerX,centerY,x,y) >radius:
                    continue
                if (0 < x < maxX and 0 < y < maxY and img[x,y][0] > 190 and img[x,y][1] > 190 and img[x,y][2] > 190):
                    numOfWhitePixels +=1
                elif (0 < x < maxX and 0 < y < maxY and img[x,y][0] < 90 and img[x,y][1] < 90 and img[x,y][2] < 90):
                    numOfBlackPixels +=1
                else:
                    numOfOtherPixels +=1
        #This section will classify what the ball is. The thresholds need to be 
        #redone on the size of the image.
        if numOfBlackPixels > 500:
            eight_ball.append((centerY,centerX,radius))
            cv2.circle(img,(int(centerY),int(centerX)),int(radius),BLACK,2)
        #There can only be one cue ball and it should be the ball with the most
        #white pixels. Some trouble due to lighting on detecting a stripe or a light
        #colored ball as the cue ball.
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
    cv2.imwrite('colors.jpeg',img)
    solids.sort(key = compare)
    stripes.sort(key = compare)
    return cue, solids, eight_ball, stripes

#This function takes in all of the different balls detected by the CV and builds
#a formatted list of them [cue, solids, eight_ball, stripes].
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

#Used to ensure that the coordinates of the balls are equal. The center of each
#ball is never exact so there is a margin for error built in.
def checkEquality(tempList, big_list):
    for i in range(2):
        for j in range(16):
            if abs(int(tempList[i][j]) - int(big_list[i][j]))>6:
                return False
    return True

def compare(ball):
  return ball[0]


#This function will run the CV system until it detects the same pool balls on the table
# two times in a row.
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
    shot_calculation.start_calc(big_list[0],big_list[1],big_list[2],big_list[3])

#Open the serial port with the arduino. Will need to change it if you change the port that is used
arduino = serial.Serial(port = '/dev/cu.usbmodem142101',baudrate=115200, timeout=0)
#Starting the video capture using the webcam of the laptop or a connected camera
imcap = cv2.VideoCapture(0) 
final_list = DetectPoolBalls()
final_list = DetectPoolBalls()
final_list = DetectPoolBalls()
final_list = DetectPoolBalls()
final_list = DetectPoolBalls()
#This loop will detect the pool balls on the pool table when it receives the correct
#signal from the arduino through serial communication
while True:
    data = arduino.readline()
    #cv2.waitKey()
    if data:
        data = data.decode()
        data = data.encode()
        #Detecting all pool balls and communicating to the shot calculation to 
        #shoot for stripes
        if data == b'1':
            print("Stripes")
            final_list = DetectPoolBalls()
            #print(final_list)
            final_list.append("Stripe")
            detect_changes(final_list, "Stripe")
            print("Stripes done")
        #Detecting all pool balls and communicating to the shot calculation to 
        #shoot for solids
        elif data ==  b'0':
            print ("Solids")
            final_list = DetectPoolBalls()
            #print(final_list)
            final_list.append("Solid")
            detect_changes(final_list,"Solid")
            print("Solids done")
        #An error has occurred in communication with the arduino. 
        # Useful for debugging
        elif data != "b''":
            print ("You Entered :", data)
cv2.destroyWindow('pool_ball_detect')