''' The Following File Contains Code for a working implementation of a pool table real time 
    optimal shot calculator'''

import math
from array import *
import cv2 as cv
import numpy as np
import pyfirmata
import time
import serial
from PIL import Image

################### GLOBAL PARAMETERS ###################
NUMBER_OF_BALLS = 16    #The total number of balls on the table
FIRST_BALL = 1          #Solid Ball 1
DISTANCES = 0           #The Index which gets the distances of each ball to each pocket
FIRST_SLOPE = 1         #The Index which gets the slope of each ball to cue ball
FIRST_INTERCEPT = 2     #The Index which gets the intercept of each ball to cue ball
SECOND_SLOPES = 3       #The Index which gets the slope of each ball to each pocket
SECOND_INTERCEPT = 4    #The Index which gets the intercept of the line of each ball to each pocket
GHOST_BALL = 5          #The point at which the cue ball will make contact with the target ball
DISTANCE_CUE = 6        #The distance from the cue ball to the target ball 
POCKETX = 0             #The Index which gets the x corrdinate of the pocket
POCKETY = 1             #The Index which gets the y corrdinate of the pocket
NUMBER_OF_PARAMS = 5    #The Number of parameters in the dictionary 
RADIUS_BALL = 25        #The Radius of each ball
RADIUS_POCKET = 41      #The Radius of  each pocket
CUE_BALL = 0            #The Cue ball Index
NO_POCKETS = 6          #The Number of Pockets on a standard pool table
BLUE = (255,0,0)        #BGR Color Representation of the Color Blue
GREEN = (0,255,0)       #BGR Color Representation of the Color Green
RED = (0,0,255)         #BGR Color Representation of the Color Red
WHITE = (255,255,255)   #BGR Color Representation of the Color White
YELLOW = (0,255,255)    #BGR Color Representation of the Color Yellow
GREY = (150,150,150)    #BGR Color Representation of the Color Grey
TABLE_X_HI = 900        #Table bottom right corner x coordinate
TABLE_X_LO = 100        #Table top left corner x coordinate
TABLE_Y_HI = 700        #Table bottom right corner y coordinate
TABLE_Y_LO = 300        #Table top left corner y coordinate
NAN = np.nan            #Not a number, used for default and non-reachable values
INF = np.inf            #Infinity, Used for the x coordinates of the balls is the same
ROOT2 = math.sqrt(2)    #The Square Root of 2
REFLECT_DIST = 100      #The Distance of the Reflection Line
DONEPIN = 8             #The Pin used to talk back to the arduino with
LAST_SOLID = 7
FIRST_STRIPE = 9
#brief: A list of the various parametrs for the ball
#int (ball number) -> list
#list = index 0 -> DISTACNE
#       index 1 -> Slope of first set of lines (cue ball to ball)
#       index 2 -> intercepts of first set of lines (cue ball to ball)
#       index 3 -> Slopes of second set of lines (ball to pockets)
#       index 4 -> intercept of second set of lines (ball to pockets)
ball_to_shots = {1: [[NAN,NAN,NAN,NAN,NAN,NAN],NAN,NAN,[NAN,NAN,NAN,NAN,NAN,NAN],[NAN,NAN,NAN,NAN,NAN,NAN],[NAN,NAN],NAN],
                2:  [[NAN,NAN,NAN,NAN,NAN,NAN],NAN,NAN,[NAN,NAN,NAN,NAN,NAN,NAN],[NAN,NAN,NAN,NAN,NAN,NAN],[NAN,NAN],NAN],
                3:  [[NAN,NAN,NAN,NAN,NAN,NAN],NAN,NAN,[NAN,NAN,NAN,NAN,NAN,NAN],[NAN,NAN,NAN,NAN,NAN,NAN],[NAN,NAN],NAN],
                4:  [[NAN,NAN,NAN,NAN,NAN,NAN],NAN,NAN,[NAN,NAN,NAN,NAN,NAN,NAN],[NAN,NAN,NAN,NAN,NAN,NAN],[NAN,NAN],NAN],
                5:  [[NAN,NAN,NAN,NAN,NAN,NAN],NAN,NAN,[NAN,NAN,NAN,NAN,NAN,NAN],[NAN,NAN,NAN,NAN,NAN,NAN],[NAN,NAN],NAN],
                6:  [[NAN,NAN,NAN,NAN,NAN,NAN],NAN,NAN,[NAN,NAN,NAN,NAN,NAN,NAN],[NAN,NAN,NAN,NAN,NAN,NAN],[NAN,NAN],NAN],
                7:  [[NAN,NAN,NAN,NAN,NAN,NAN],NAN,NAN,[NAN,NAN,NAN,NAN,NAN,NAN],[NAN,NAN,NAN,NAN,NAN,NAN],[NAN,NAN],NAN],
                8:  [[NAN,NAN,NAN,NAN,NAN,NAN],NAN,NAN,[NAN,NAN,NAN,NAN,NAN,NAN],[NAN,NAN,NAN,NAN,NAN,NAN],[NAN,NAN],NAN],
                9:  [[NAN,NAN,NAN,NAN,NAN,NAN],NAN,NAN,[NAN,NAN,NAN,NAN,NAN,NAN],[NAN,NAN,NAN,NAN,NAN,NAN],[NAN,NAN],NAN],
                10: [[NAN,NAN,NAN,NAN,NAN,NAN],NAN,NAN,[NAN,NAN,NAN,NAN,NAN,NAN],[NAN,NAN,NAN,NAN,NAN,NAN],[NAN,NAN],NAN],
                11: [[NAN,NAN,NAN,NAN,NAN,NAN],NAN,NAN,[NAN,NAN,NAN,NAN,NAN,NAN],[NAN,NAN,NAN,NAN,NAN,NAN],[NAN,NAN],NAN],
                12: [[NAN,NAN,NAN,NAN,NAN,NAN],NAN,NAN,[NAN,NAN,NAN,NAN,NAN,NAN],[NAN,NAN,NAN,NAN,NAN,NAN],[NAN,NAN],NAN],
                13: [[NAN,NAN,NAN,NAN,NAN,NAN],NAN,NAN,[NAN,NAN,NAN,NAN,NAN,NAN],[NAN,NAN,NAN,NAN,NAN,NAN],[NAN,NAN],NAN],
                14: [[NAN,NAN,NAN,NAN,NAN,NAN],NAN,NAN,[NAN,NAN,NAN,NAN,NAN,NAN],[NAN,NAN,NAN,NAN,NAN,NAN],[NAN,NAN],NAN],
                15: [[NAN,NAN,NAN,NAN,NAN,NAN],NAN,NAN,[NAN,NAN,NAN,NAN,NAN,NAN],[NAN,NAN,NAN,NAN,NAN,NAN],[NAN,NAN],NAN]}

#the maximum and minimum x the ball will be able to take after a shot
balls_to_x_boundary = {1:   [NAN,NAN],
                    2:      [NAN,NAN],
                    3:      [NAN,NAN],
                    4:      [NAN,NAN],
                    5:      [NAN,NAN],
                    6:      [NAN,NAN],
                    7:      [NAN,NAN],
                    8:      [NAN,NAN],
                    9:      [NAN,NAN],
                    10:     [NAN,NAN],
                    11:     [NAN,NAN],
                    12:     [NAN,NAN],
                    13:     [NAN,NAN],
                    14:     [NAN,NAN],
                    15:     [NAN,NAN]}

#themaximum and minimum y the ball will be able to take after a shot
balls_to_y_boundary = {1:   [NAN,NAN],
                    2:      [NAN,NAN],
                    3:      [NAN,NAN],
                    4:      [NAN,NAN],
                    5:      [NAN,NAN],
                    6:      [NAN,NAN],
                    7:      [NAN,NAN],
                    8:      [NAN,NAN],
                    9:      [NAN,NAN],
                    10:     [NAN,NAN],
                    11:     [NAN,NAN],
                    12:     [NAN,NAN],
                    13:     [NAN,NAN],
                    14:     [NAN,NAN],
                    15:     [NAN,NAN]}

# the chosen pocket for each ball along with its hardness
pocket_for_each_ball = [[NAN,INF],[NAN,INF],[NAN,INF],[NAN,INF],[NAN,INF],
                        [NAN,INF],[NAN,INF],[NAN,INF],[NAN,INF],[NAN,INF],
                        [NAN,INF],[NAN,INF],[NAN,INF],[NAN,INF],[NAN,INF]]


#A list of pockets with each element being an x-y coordinate for the pocket
pockets = [[0,0],[600,0],[1200,0],[1200,600],[600,600],[0,600]]
center_edges = [[NAN,NAN],[NAN,NAN],[NAN,NAN],[NAN,NAN],[NAN,NAN],[NAN,NAN]]

#A list of X and Y coordinates for each ball
listX = [600,600,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1]
listY = [500,100,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1]


def calc_center_edges():
    global center_edges
    p0 = center_edges[0]
    p1 = center_edges[1]
    p2 = center_edges[2]
    p3 = center_edges[3]
    p4 = center_edges[4]
    p5 = center_edges[5]
    p0[0] = pockets[0][0] + (RADIUS_POCKET/ROOT2)
    p0[1] = pockets[0][1] + (RADIUS_POCKET/ROOT2)
    p1[0] = pockets[1][0] 
    p1[1] = pockets[1][1] + (RADIUS_POCKET/ROOT2)
    p2[0] = pockets[2][0] - (RADIUS_POCKET/ROOT2)
    p2[1] = pockets[2][1] + (RADIUS_POCKET/ROOT2)
    p3[0] = pockets[3][0] - (RADIUS_POCKET/ROOT2)
    p3[1] = pockets[3][1] - (RADIUS_POCKET/ROOT2)
    p4[0] = pockets[4][0] 
    p4[1] = pockets[4][1] - (RADIUS_POCKET/ROOT2)
    p5[0] = pockets[5][0] + (RADIUS_POCKET/ROOT2)
    p5[1] = pockets[5][1] - (RADIUS_POCKET/ROOT2)

#board to connect the arduino to 
board = pyfirmata.Arduino('/dev/cu.usbmodem141101') 
arduino = serial.Serial(port = '/dev/cu.usbmodem141101',baudrate=115200, timeout=0)


################### Collision Check  ###################
#taken from: https://www.jeffreythompson.org/collision-detection/line-circle.php

# Definition: Checks if the line given bt (x0,y0) and (x1,y1) lies on the circle given by (cx,cy) and radius
# Return Value: True if the line interesects at one point or two, False if not
# Errors: NA
def checkCollision(x1,y1,x2,y2,cx,cy,r):

    #is either end INSIDE the circle?
    #if so, return true immediately
    inside1 = pointCircle(x1,y1, cx,cy,r)
    inside2 = pointCircle(x2,y2, cx,cy,r)
    if (inside1 or inside2): return True

    #get length of the line
    distX = x1 - x2
    distY = y1 - y2
    len = math.sqrt( (distX*distX) + (distY*distY) )

    #get dot product of the line and circle
    dot = ( ((cx-x1)*(x2-x1)) + ((cy-y1)*(y2-y1)) ) / pow(len,2)

    #find the closest point on the line
    closestX = x1 + (dot * (x2-x1))
    closestY = y1 + (dot * (y2-y1))

    # is this point actually on the line segment?
    # if so keep going, but if not, return false
    onSegment = linePoint(x1,y1,x2,y2, closestX,closestY)
    if (not onSegment): return False
    #get distance to closest point
    distX = closestX - cx
    distY = closestY - cy
    distance = math.sqrt((distX*distX)+(distY*distY))

    if (distance <= r): return True
    else: return False


#taken from: https://www.jeffreythompson.org/collision-detection/line-circle.php
#OINT/CIRCLE
def pointCircle(px,py,cx,cy,r):
    #get distance between the point and circle's center
    #using the Pythagorean Theorem
    distX = px - cx
    distY = py - cy
    distance = math.sqrt( (distX*distX) + (distY*distY) )

    #if the distance is less than the circle's
    # radius the point is inside!
    if (distance <= r): return True
    else: return False


#taken from: https://www.jeffreythompson.org/collision-detection/line-circle.php
# LINE/POINT
def linePoint(x1,y1,x2,y2,px,py):
    # get distance from the point to the two ends of the line
    d1 = math.sqrt(((px-x1)*(px-x1)) + ((py-y1)*(py-y1)))
    d2 = math.sqrt(((px-x2)*(px-x2)) + ((py-y2)*(py-y2)))

    # get the length of the line
    lineLen =math.sqrt(((x1-x2)*(x1-x2)) + ((y1-y2)*(y1-y2)))


    # since floats are so minutely accurate, add
    # a little buffer zone that will give collision
    buffer = 0.001    # higher # = less accurate

    # if the two distances are equal to the line's
    # length, the point is on the line!
    # note we use the buffer here to give a range,
    # rather than one #
    if (d1+d2 >= lineLen-buffer and d1+d2 <= lineLen+buffer): return True
    else: return False

#breif: Print helper Function for clarity of Code
def print_dimensions():
    for i in range(FIRST_BALL,NUMBER_OF_BALLS):
        if(listX[i]<0): continue
        shot_params = ball_to_shots.get(i)
        x_bound = balls_to_x_boundary.get(i)
        y_bound = balls_to_y_boundary.get(i)
        print("For Ball {index}".format(index = i))
        print("Dimensions are {x},{y}".format(x = listX[i], y = listY[i]))
        print("Distances to Each Pocket = {distance}".format(distance = shot_params[DISTANCES]))
        print("First Slope = {slope}".format(slope = shot_params[FIRST_SLOPE]))
        print("First Intercept = {intercept}".format(intercept = shot_params[FIRST_INTERCEPT]))
        print("Second Slopes = {slopes}".format(slopes = shot_params[SECOND_SLOPES]))
        print("Second Intercepts = {intercepts}".format(intercepts = shot_params[SECOND_INTERCEPT]))
        print("Bounday X Values are = {bound}".format(bound = x_bound))
        print("Bounday Y Values are = {bound}".format(bound = y_bound))
        print("Pocket Chosen for this ball and its hardness = {pocket}".format(pocket = pocket_for_each_ball[i-1]))
        print("Ghost Coordinates for this ball are = {coords}".format(coords = shot_params[GHOST_BALL]))
        print("Distance from Cue Ball to target Ball = {dist}".format(dist = shot_params[DISTANCE_CUE]))
        print("-------------------------------------------------")

def find_distance_to_cue_ball():
    for target_ball in range(FIRST_BALL,NUMBER_OF_BALLS):
        shot_params = ball_to_shots.get(target_ball)
        if (listX[target_ball]<0 or listY[target_ball]<0): 
            shot_params[DISTANCE_CUE] = NAN
            continue
        dist = distance(listX[CUE_BALL],listY[CUE_BALL],listX[target_ball],listY[target_ball])
        shot_params[DISTANCE_CUE] = dist


#brief: Finds the distance of each ball to each pocket and stores it in the dictionary 
def find_distance_to_all_pockets():
    for i in range(FIRST_BALL,NUMBER_OF_BALLS):
        if(listX[i]<0): continue
        shot_params = ball_to_shots.get(i)
        pocket_idx = 0
        for pocket in center_edges:
            distanceX = (listX[i] - pocket[POCKETX]) * (listX[i] - pocket[POCKETX])
            distanceY = (listY[i] - pocket[POCKETY]) * (listY[i] - pocket[POCKETY])
            dist = math.sqrt(distanceX + distanceY)
            shot_params[DISTANCES][pocket_idx] = dist
            pocket_idx+=1

#brief: Checks if the shot between the cue ball and the target ball is possible. If so
#       the value is stored in the Dictionary
def create_first_lines():
    #cue ball has been pocketed, remove all existing lines
    if(listX[CUE_BALL]<0 or listY[CUE_BALL]<0):
        for i in range(FIRST_BALL,NUMBER_OF_BALLS):
            shot_params = ball_to_shots.get(i)
            shot_params[FIRST_SLOPE] = NAN
            shot_params[FIRST_INTERCEPT] = NAN
        return
    for target_ball in range(FIRST_BALL,NUMBER_OF_BALLS):
        #check if ball has been potted
        if(listX[target_ball]<0 or listY[target_ball]<0): 
            shot_params = ball_to_shots.get(target_ball)
            shot_params[FIRST_SLOPE] = NAN
            shot_params[FIRST_INTERCEPT] = NAN
            continue
        #check if there exists a collision between the cue ball and this ball for everyball 
        # but itself 
        collision = False
        for collision_ball in range(FIRST_BALL,NUMBER_OF_BALLS):
            if (target_ball == collision_ball): continue
            if (listX[collision_ball]<0): continue
            if (listY[collision_ball]<0): continue
            upperCheck = checkCollision(listX[CUE_BALL],listY[CUE_BALL]+RADIUS_BALL,listX[target_ball],listY[target_ball]+RADIUS_BALL,listX[collision_ball],listY[collision_ball],RADIUS_BALL)
            lowerCheck = checkCollision(listX[CUE_BALL],listY[CUE_BALL]-RADIUS_BALL,listX[target_ball],listY[target_ball]-RADIUS_BALL,listX[collision_ball],listY[collision_ball],RADIUS_BALL)
            #shot is not possible
            if (upperCheck or lowerCheck):
                collision = True
                break
        #no collision shot is possible
        if(not collision):
            if (listX[target_ball]==listX[CUE_BALL]): slope = INF
            else: slope = (listY[target_ball]-listY[CUE_BALL])/(listX[target_ball]-listX[CUE_BALL])
            if (slope == INF): intercept = INF
            else: intercept = listY[target_ball] - (slope * listX[target_ball])
        #shot is not possible cause collision 
        else:
            slope = NAN
            intercept = NAN
        shot_params = ball_to_shots.get(target_ball)
        shot_params[FIRST_SLOPE] = slope
        shot_params[FIRST_INTERCEPT] = intercept

#brief: Checks if the shot between the cue ball and each pocket ball is possible. If so
#       the value is stored in the Dictionary
def create_second_lines():
    #first go though all balls, 
    #for each ball check if first line is non nan
    #if not nan, check for each pocket without collisions and store that value
    for target_ball in range(FIRST_BALL, NUMBER_OF_BALLS):
        if(listX[target_ball]<0): continue
        if(listY[target_ball]<0): continue
        shot_params = ball_to_shots.get(target_ball)
        if(math.isnan(shot_params[FIRST_SLOPE])): 
            for pocket in range(NO_POCKETS):
                shot_params[SECOND_SLOPES][pocket] = NAN
                shot_params[SECOND_INTERCEPT][pocket] = NAN
            continue
        if(math.isnan(shot_params[FIRST_INTERCEPT])):
            for pocket in range(NO_POCKETS):
                shot_params[SECOND_SLOPES][pocket] = NAN
                shot_params[SECOND_INTERCEPT][pocket] = NAN
            continue
        #create a line for each pocket
        pocket_index = 0;
        for pocket in center_edges:
            collision = False
            #check collision for that pocket with every ball
            for collision_ball in range(CUE_BALL, NUMBER_OF_BALLS):
                if (collision_ball == target_ball): continue
                if (listX[collision_ball]<0): continue
                if (listY[collision_ball]<0): continue
                upperCheck = checkCollision(listX[target_ball],listY[target_ball]+RADIUS_BALL,pocket[POCKETX],pocket[POCKETY]+RADIUS_POCKET,listX[collision_ball],listY[collision_ball],RADIUS_BALL)
                lowerCheck = checkCollision(listX[target_ball],listY[target_ball]-RADIUS_BALL,pocket[POCKETX],pocket[POCKETY]-RADIUS_POCKET,listX[collision_ball],listY[collision_ball],RADIUS_BALL)
                if (upperCheck or lowerCheck): 
                    collision = True
                    break
            # a successful shot can be made to that pocket
            if(not collision):
                if (listX[target_ball] == pocket[POCKETX]): slope = INF
                else: slope = (pocket[POCKETY] - listY[target_ball])/(pocket[POCKETX] - listX[target_ball])
                if (slope == INF): intercept = INF
                else: intercept = pocket[POCKETY] - (slope * pocket[POCKETX])
                shot_params[SECOND_SLOPES][pocket_index] = slope
                shot_params[SECOND_INTERCEPT][pocket_index] = intercept
            # a successful shot canot be made to that pocket
            else:
                shot_params[SECOND_SLOPES][pocket_index] = NAN
                shot_params[SECOND_INTERCEPT][pocket_index] = NAN
            pocket_index+=1

#brief: Draws the image that is going to be projected onto the pool table
def drawImage(choice):
    img = np.zeros((800,1400,3), np.uint8)
    cv.rectangle (img,(100,100),(1300,700),GREEN,1)
    for target_ball in range(NUMBER_OF_BALLS):
        if listX[target_ball]>0:
            if (target_ball==CUE_BALL):
                cv.circle(img,(listX[target_ball]+100,listY[target_ball]+100),RADIUS_BALL,WHITE,-1)
            else:
                cv.circle(img,(listX[target_ball]+100,listY[target_ball]+100),RADIUS_BALL,YELLOW,-1)
    for pocket in pockets:
        cv.circle(img,(pocket[0]+100,pocket[1]+100),RADIUS_POCKET,BLUE,-1)   
    chosen_shot = choose_easiest_shot(choice)
    print("Chosen Shot = {c}".format(c = chosen_shot))
    if (chosen_shot>=0):
        shot_params = ball_to_shots.get(chosen_shot+1)
        cv.line(img,(listX[CUE_BALL]+100,listY[CUE_BALL]+100),(int(shot_params[GHOST_BALL][0]+100),int(shot_params[GHOST_BALL][1]+100)),RED,2)
        cv.circle(img,(shot_params[GHOST_BALL][0]+100,shot_params[GHOST_BALL][1]+100),RADIUS_BALL,WHITE,1)
        pocketX = int(center_edges[pocket_for_each_ball[chosen_shot][0]][POCKETX])
        pocketY = int(center_edges[pocket_for_each_ball[chosen_shot][0]][POCKETY])
        m = 0
        if (listX[chosen_shot+1]==pocketX): m = INF
        else: 
            m = (listY[chosen_shot+1]-pocketY)/(listX[chosen_shot+1]-pocketX)
        new_slope = -1/m
        theta = math.atan(new_slope)
        newX = shot_params[GHOST_BALL][0] + int(REFLECT_DIST * math.cos(theta))
        newY = shot_params[GHOST_BALL][1] + int(REFLECT_DIST * math.sin(theta))
        #cv.line(img,(shot_params[GHOST_BALL][0],shot_params[GHOST_BALL][1]),(newX,newY),GREY,2)
        cv.line(img,(listX[chosen_shot+1]+100,listY[chosen_shot+1]+100),(pocketX+100,pocketY+100),RED,2)
    cv.imwrite('ghost.jpeg',img)
    im = Image.open("ghost.jpeg")
    im_rotate = im.rotate(2)
    im_rotate.show()
    im_rotate.save('ghost.jpeg')


def find_edges():
    if(listX[CUE_BALL]<0 or listY[CUE_BALL]<0): return
    for target_ball in range(FIRST_BALL,NUMBER_OF_BALLS):
        if(listX[target_ball]<0 or listY[target_ball]<0): continue
        shot_params=ball_to_shots.get(target_ball)
        if(math.isnan(shot_params[FIRST_SLOPE])):
            y_bound = balls_to_y_boundary.get(target_ball)
            x_bound = balls_to_x_boundary.get(target_ball)
            x_bound = [NAN,NAN]
            y_bound = [NAN,NAN]
            continue
        elif(math.isinf(shot_params[FIRST_SLOPE])): 
            tangent_slope = 0
            y_bound = balls_to_y_boundary.get(target_ball)
            if(listY[CUE_BALL] > listY[target_ball]):
                y_bound[0] = TABLE_Y_LO
                y_bound[1] = listY[target_ball]
            else:
                y_bound[0] = listY[target_ball]
                y_bound[1] = TABLE_Y_HI
            x_bound = balls_to_x_boundary.get(target_ball)
            x_bound[0] = TABLE_X_LO
            x_bound[1] = TABLE_X_HI
        elif(shot_params[FIRST_SLOPE]==0):
            y_bound = balls_to_y_boundary.get(target_ball)
            x_bound = balls_to_x_boundary.get(target_ball)
            if(listX[CUE_BALL] > listX[target_ball]):
                x_bound[0] = TABLE_X_LO
                x_bound[1] = listX[target_ball]
            else:
                x_bound[0] = listX[target_ball]
                x_bound[1] = TABLE_X_HI
            y_bound[0] = TABLE_Y_LO
            y_bound[1] = TABLE_Y_HI
        else:
            tangent_slope = -1/shot_params[FIRST_SLOPE]
            new_line_b = listY[target_ball] - (tangent_slope*listX[target_ball])
            new_x = (TABLE_Y_LO - new_line_b)/tangent_slope
            if(new_x>TABLE_X_HI) : new_x = TABLE_X_HI
            elif(new_x<TABLE_X_LO) : new_x = TABLE_X_LO
            x_bound = balls_to_x_boundary.get(target_ball)
            x_bound[0] = new_x
            new_x = (TABLE_Y_HI - new_line_b)/tangent_slope
            if(new_x>TABLE_X_HI) : new_x = TABLE_X_HI
            elif(new_x<TABLE_X_LO) : new_x = TABLE_X_LO
            x_bound[1] = new_x
            y_bound = balls_to_y_boundary.get(target_ball)
            new_y = (tangent_slope * TABLE_X_LO) + new_line_b
            if(new_y>TABLE_Y_HI) : new_y = TABLE_Y_HI
            elif(new_y<TABLE_Y_LO) : new_y = TABLE_Y_LO
            y_bound[0] = new_y
            new_y = (tangent_slope * TABLE_X_HI) + new_line_b
            if(new_y>TABLE_Y_HI) : new_y = TABLE_Y_HI
            elif(new_y<TABLE_Y_LO) : new_y = TABLE_Y_LO
            y_bound[1] = new_y

#@TODO: Now FIGURE OUT HOW TO CHOOSE A POCKET

#not fully correct
def remove_impossible_pockets():
    if(listX[CUE_BALL]<0 or listY[CUE_BALL]<0): return
    for target_ball in range(FIRST_BALL, NUMBER_OF_BALLS):
        if(listX[target_ball]<0 or listY[target_ball]<0): 
            continue
        shot_params=ball_to_shots.get(target_ball)
        x_bounds = balls_to_x_boundary.get(target_ball)
        y_bounds = balls_to_y_boundary.get(target_ball)
        if(listX[CUE_BALL] == listX[target_ball]):
            pocket_idx = 0
            for pocket in center_edges: 
                if(pocket[POCKETY]<listY[target_ball] and listY[CUE_BALL]<listY[target_ball]):
                    shot_params[DISTANCES][pocket_idx] = NAN
                    shot_params[SECOND_SLOPES][pocket_idx] = NAN
                    shot_params[SECOND_INTERCEPT][pocket_idx] = NAN
                elif(pocket[POCKETY]>listY[target_ball] and listY[CUE_BALL]>listY[target_ball]):
                    shot_params[DISTANCES][pocket_idx] = NAN
                    shot_params[SECOND_SLOPES][pocket_idx] = NAN
                    shot_params[SECOND_INTERCEPT][pocket_idx] = NAN
                pocket_idx+=1
        elif(listX[CUE_BALL]<listX[target_ball]):
            pocket_idx = 0
            for pocket in center_edges: 
                if (pocket_idx<3):
                    if(pocket[POCKETX]<x_bounds[0]):
                        shot_params[DISTANCES][pocket_idx] = NAN
                        shot_params[SECOND_SLOPES][pocket_idx] = NAN
                        shot_params[SECOND_INTERCEPT][pocket_idx] = NAN
                else:
                    if(pocket[POCKETX]<x_bounds[1]):
                        shot_params[DISTANCES][pocket_idx] = NAN
                        shot_params[SECOND_SLOPES][pocket_idx] = NAN
                        shot_params[SECOND_INTERCEPT][pocket_idx] = NAN
                pocket_idx+=1
        elif(listX[CUE_BALL]>listX[target_ball]):
            pocket_idx = 0
            for pocket in center_edges:
                if (pocket_idx<3):
                    if(pocket[POCKETX]>x_bounds[0]):
                        shot_params[DISTANCES][pocket_idx] = NAN
                        shot_params[SECOND_SLOPES][pocket_idx] = NAN
                        shot_params[SECOND_INTERCEPT][pocket_idx] = NAN
                else:
                    if(pocket[POCKETX]>x_bounds[1]):
                        shot_params[DISTANCES][pocket_idx] = NAN
                        shot_params[SECOND_SLOPES][pocket_idx] = NAN
                        shot_params[SECOND_INTERCEPT][pocket_idx] = NAN
                pocket_idx+=1
            
        elif(listY[CUE_BALL]==listY[target_ball]):
            pocket_idx = 0
            for pocket in center_edges: 
                if(pocket[POCKETX]<listX[target_ball] and listX[CUE_BALL]<listX[target_ball]):
                    shot_params[DISTANCES][pocket_idx] = NAN
                    shot_params[SECOND_SLOPES][pocket_idx] = NAN
                    shot_params[SECOND_INTERCEPT][pocket_idx] = NAN
                elif(pocket[POCKETX]>listX[target_ball] and listX[CUE_BALL]>listX[target_ball]):
                    shot_params[DISTANCES][pocket_idx] = NAN
                    shot_params[SECOND_SLOPES][pocket_idx] = NAN
                    shot_params[SECOND_INTERCEPT][pocket_idx] = NAN
                pocket_idx+=1
        elif (listY[CUE_BALL] > listY[target_ball]):
            pocket_idx = 0
            for pocket in center_edges:
                if (pocket_idx<3):
                    if(pocket[POCKETY]>y_bounds[0]):
                        shot_params[DISTANCES][pocket_idx] = NAN
                        shot_params[SECOND_SLOPES][pocket_idx] = NAN
                        shot_params[SECOND_INTERCEPT][pocket_idx] = NAN
                else:
                    if(pocket[POCKETY]>y_bounds[1]):
                        shot_params[DISTANCES][pocket_idx] = NAN
                        shot_params[SECOND_SLOPES][pocket_idx] = NAN
                        shot_params[SECOND_INTERCEPT][pocket_idx] = NAN
                pocket_idx+=1
        elif (listY[CUE_BALL] < listY[target_ball]):
            pocket_idx = 0
            for pocket in center_edges:
                if (pocket_idx<3):
                    if(pocket[POCKETY]<y_bounds[0]):
                        shot_params[DISTANCES][pocket_idx] = NAN
                        shot_params[SECOND_SLOPES][pocket_idx] = NAN
                        shot_params[SECOND_INTERCEPT][pocket_idx] = NAN
                else:
                    if(pocket[POCKETY]<y_bounds[1]):
                        shot_params[DISTANCES][pocket_idx] = NAN
                        shot_params[SECOND_SLOPES][pocket_idx] = NAN
                        shot_params[SECOND_INTERCEPT][pocket_idx] = NAN
                pocket_idx+=1
           
            
        

def choose_pocket():
    if(listX[CUE_BALL]<0 or listY[CUE_BALL]<0): return
    for target_ball in range(FIRST_BALL, NUMBER_OF_BALLS):
        if(listX[target_ball]<0 or listY[target_ball]<0): 
            pocket_for_each_ball[target_ball-1][0] = NAN
            pocket_for_each_ball[target_ball-1][1] = INF
            continue
        shot_params=ball_to_shots.get(target_ball)
        if(math.isnan(shot_params[FIRST_SLOPE])): 
            pocket_for_each_ball[target_ball-1][0] = NAN
            pocket_for_each_ball[target_ball-1][1] = INF
            continue
        second_slopes = shot_params[SECOND_SLOPES]
        first_slope = shot_params[FIRST_SLOPE]
        distances = shot_params[DISTANCES]
        dist_cue = shot_params[DISTANCE_CUE]
        hardness_all_shots = [NAN,NAN,NAN,NAN,NAN,NAN]
        viable = False
        for idx in range(NO_POCKETS):
            if(math.isnan(second_slopes[idx])): continue
            if(math.isnan(distances[idx])): continue
            m = second_slopes[idx]
            dist = 2 * RADIUS_BALL
            if (not math.isinf(m) and m != 0):
                theta = math.atan(m)
                xdelta = dist * math.cos(theta)
                ydelta = dist * math.sin(theta)
                dist1 = distance(center_edges[idx][POCKETX],center_edges[idx][POCKETY],listX[target_ball]+xdelta,listY[target_ball]+ydelta)
                dist2 = distance(center_edges[idx][POCKETX],center_edges[idx][POCKETY],listX[target_ball]-xdelta,listY[target_ball]-ydelta)
                if(dist1<dist2):
                    xGhost = listX[target_ball] - xdelta
                    yGhost = listY[target_ball] - ydelta
                else:
                    xGhost = listX[target_ball] + xdelta
                    yGhost = listY[target_ball] + ydelta
            elif (math.isinf(m)):
                xdelta = 0
                ydelta = dist
                xGhost = listX[target_ball]
                if (center_edges[idx][POCKETY]<listY[target_ball]):
                    yGhost = listY[target_ball] + ydelta
                else:
                     yGhost = listY[target_ball] - ydelta
            else:
                ydelta = 0
                xdelta = dist
                yGhost = listY[target_ball]
                if (center_edges[idx][POCKETX]<listX[target_ball]):
                    xGhost = listY[target_ball] + xdelta
                else:
                    xGhost = listY[target_ball] - xdelta
            
            collision = False
            #now that we have ghost coordinates check for collisions
            for collision_ball in range(FIRST_BALL,NUMBER_OF_BALLS):
                if (target_ball == collision_ball): continue
                if (listX[collision_ball]<0): continue
                if (listY[collision_ball]<0): continue
                upperCheck = checkCollision(listX[CUE_BALL],listY[CUE_BALL]+RADIUS_BALL,xGhost,yGhost+RADIUS_BALL,listX[collision_ball],listY[collision_ball],RADIUS_BALL)
                lowerCheck = checkCollision(listX[CUE_BALL],listY[CUE_BALL]-RADIUS_BALL,xGhost,yGhost-RADIUS_BALL,listX[collision_ball],listY[collision_ball],RADIUS_BALL)
                #shot is not possible
                if (upperCheck or lowerCheck):
                    collision = True
                    break
            if(collision): 
                continue
            viable = True
            calc_dist = distances[idx] * 3
            calc_dist_2 = dist_cue * 3
            if(math.isinf(first_slope)):
                if(math.isinf(second_slopes[idx]) or second_slopes[idx]==1):
                    calc_slope_delta = 0
                else:
                    calc_slope_delta = abs(second_slopes[idx]) * 2.5
            else:
                if(math.isinf(second_slopes[idx])):
                    calc_slope_delta = 0
                else:
                    calc_slope_delta = abs(second_slopes[idx] - first_slope) * 2.5
            total_hardness = calc_dist * calc_slope_delta
            hardness_all_shots[idx] = total_hardness
        #shot can be made chose best
        if (viable):
            shot_idx = 0
            chosen_idx = -1
            min_calc = 100000000
            for hardness in hardness_all_shots:
                if (math.isnan(hardness)): 
                    shot_idx+=1
                    continue
                else:
                    if (min_calc>hardness):
                        min_calc = hardness
                        chosen_idx = shot_idx
                    shot_idx+=1
            pocket_for_each_ball[target_ball-1][0] = chosen_idx
            pocket_for_each_ball[target_ball-1][1] = min_calc
            m = second_slopes[chosen_idx]
            dist = 2 * RADIUS_BALL
            theta = math.atan(m)
            xdelta = dist * math.cos(theta)
            ydelta = dist * math.sin(theta)
            dist1 = distance(center_edges[chosen_idx][POCKETX],center_edges[chosen_idx][POCKETY],listX[target_ball]+xdelta,listY[target_ball]+ydelta)
            dist2 = distance(center_edges[chosen_idx][POCKETX],center_edges[chosen_idx][POCKETY],listX[target_ball]-xdelta,listY[target_ball]-ydelta)
            if(dist1<dist2):
                xGhost = listX[target_ball] - xdelta
                yGhost = listY[target_ball] - ydelta
            else:
                xGhost = listX[target_ball] + xdelta
                yGhost = listY[target_ball] + ydelta
            shot_params[GHOST_BALL][0] = int(xGhost)
            shot_params[GHOST_BALL][1] = int(yGhost)
        else: 
            shot_params[GHOST_BALL][0] = NAN
            shot_params[GHOST_BALL][1] = NAN
            pocket_for_each_ball[target_ball-1][0] = NAN
            pocket_for_each_ball[target_ball-1][1] = INF
            
def choose_easiest_shot(choice):
    if(choice == "Solid"):
        min_hardness = INF
        min_indx = -1
        for idx in range(FIRST_BALL,LAST_SOLID+1):
            shot = pocket_for_each_ball[idx-1]
            if (not math.isnan(shot[0])): 
                if shot[1] < min_hardness:
                    min_hardness = shot[1]
                    min_indx = idx
        return min_indx
    else:
        min_hardness = INF
        min_indx = -1
        cur_indx = FIRST_STRIPE
        for idx in range(FIRST_STRIPE,NUMBER_OF_BALLS):
            shot = pocket_for_each_ball[idx-1]
            if (not math.isnan(shot[0])): 
                if shot[1] < min_hardness:
                    min_hardness = shot[1]
                    min_indx = idx
        return min_indx

def distance(x0,y0,x1,y1):
    distX = x0-x1
    distY = y0-y1
    distance = math.sqrt((distX*distX)+(distY*distY))
    return distance

#starts the api for the shot calculation
def start_calc(lX,lY,bottomRight,choice):
    print("calculating")
    xScale = bottomRight[0]/1200
    yScale = bottomRight[1]/600
    #print_dimensions()
    #print("Old List X = {lx}".format(lx = listX))
    #print("Old List Y = {lx}".format(lx = listY))
    for target_ball in range(CUE_BALL,NUMBER_OF_BALLS):
        listX[target_ball] = int(lX[target_ball] / xScale)
        listY[target_ball] = int(lY[target_ball] / yScale)
    #print("New List X = {lx}".format(lx = listX))
    #print("New List X = {lx}".format(lx = listY))
    calc_center_edges()
    find_distance_to_all_pockets()
    create_first_lines()
    create_second_lines()
    find_edges()
    remove_impossible_pockets()
    choose_pocket()
    print_dimensions()
    print("Choice = {c}".format(c = choice))
    print("Pockets for Each Ball are = {p}".format(p = pocket_for_each_ball))
    drawImage(choice)
    arduino.write(bytes("2", 'utf-8'))
    #board.digital[DONEPIN].write(1)
    #time.sleep(1)
    #board.digital[DONEPIN].write(0)