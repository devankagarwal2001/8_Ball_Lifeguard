#Author: Devank Agarwal, devanka@andrew.cmu.edu

''' The Following File Contains Code for a working implementation of a pool table real time 
    optimal shot calculator'''

import math
from array import *
import cv2 as cv
import numpy as np

#MACROS FOR ME TO USE
NUMBER_OF_BALLS = 16    #The total number of balls on the table
FIRST_BALL = 1          #Solid Ball 1
DISTANCES = 0           #The Index which gets the distances of each ball to each pocket
FIRST_SLOPE = 1         #The Index which gets the slope of each ball to cue ball
FIRST_INTERCEPT = 2     #The Index which gets the intercept of each ball to cue ball
SECOND_SLOPES = 3       #The Index which gets the slope of each ball to each pocket
SECOND_INTERCEPT = 4    #The Index which gets the intercept of the line of each ball to each pocket
POCKETX = 0             #The Index which gets the x corrdinate of the pocket
POCKETY = 1             #The Index which gets the y corrdinate of the pocket
NUMBER_OF_PARAMS = 5    #The Number of parameters in the dictionary 
RADIUS_BALL = 1         #The Radius of each ball
RADIUS_POCKET = 2       #The Radius of  each pocket
CUE_BALL = 0            #The Cue ball Index
NO_POCKETS = 6          #The Number of Pockets on a standard pool table
BLUE = (255,0,0)        #BGR Color Representation of the Color Blue
GREEN = (0,255,0)       #BGR Color Representation of the Color Green
RED = (0,0,255)         #BGR Color Representation of the Color Red
WHITE = (255,255,255)   #BGR Color Representation of the Color White
YELLOW = (0,255,255)    #BGR Color Representation of the Color Yellow
TABLE_X_HI = 900
TABLE_X_LO = 100
TABLE_Y_HI = 700
TABLE_Y_LO = 300

#int (ball number) -> list
#list = index 0 -> DISTACNE
#       index 1 -> Slope of first set of lines (cue ball to ball)
#       index 2 -> intercepts of first set of lines (cue ball to ball)
#       index 3 -> Slopes of second set of lines (ball to pockets)
#       index 4 -> intercept of second set of lines (ball to pockets)

ball_to_shots = {1: [[-1,-1,-1,-1,-1,-1],-1,-1,[-1,-1,-1,-1,-1,-1],[-1,-1,-1,-1,-1,-1]],
                2:  [[-1,-1,-1,-1,-1,-1],-1,-1,[-1,-1,-1,-1,-1,-1],[-1,-1,-1,-1,-1,-1]],
                3:  [[-1,-1,-1,-1,-1,-1],-1,-1,[-1,-1,-1,-1,-1,-1],[-1,-1,-1,-1,-1,-1]],
                4:  [[-1,-1,-1,-1,-1,-1],-1,-1,[-1,-1,-1,-1,-1,-1],[-1,-1,-1,-1,-1,-1]],
                5:  [[-1,-1,-1,-1,-1,-1],-1,-1,[-1,-1,-1,-1,-1,-1],[-1,-1,-1,-1,-1,-1]],
                6:  [[-1,-1,-1,-1,-1,-1],-1,-1,[-1,-1,-1,-1,-1,-1],[-1,-1,-1,-1,-1,-1]],
                7:  [[-1,-1,-1,-1,-1,-1],-1,-1,[-1,-1,-1,-1,-1,-1],[-1,-1,-1,-1,-1,-1]],
                8:  [[-1,-1,-1,-1,-1,-1],-1,-1,[-1,-1,-1,-1,-1,-1],[-1,-1,-1,-1,-1,-1]],
                9:  [[-1,-1,-1,-1,-1,-1],-1,-1,[-1,-1,-1,-1,-1,-1],[-1,-1,-1,-1,-1,-1]],
                10: [[-1,-1,-1,-1,-1,-1],-1,-1,[-1,-1,-1,-1,-1,-1],[-1,-1,-1,-1,-1,-1]],
                11: [[-1,-1,-1,-1,-1,-1],-1,-1,[-1,-1,-1,-1,-1,-1],[-1,-1,-1,-1,-1,-1]],
                12: [[-1,-1,-1,-1,-1,-1],-1,-1,[-1,-1,-1,-1,-1,-1],[-1,-1,-1,-1,-1,-1]],
                13: [[-1,-1,-1,-1,-1,-1],-1,-1,[-1,-1,-1,-1,-1,-1],[-1,-1,-1,-1,-1,-1]],
                14: [[-1,-1,-1,-1,-1,-1],-1,-1,[-1,-1,-1,-1,-1,-1],[-1,-1,-1,-1,-1,-1]],
                15: [[-1,-1,-1,-1,-1,-1],-1,-1,[-1,-1,-1,-1,-1,-1],[-1,-1,-1,-1,-1,-1]]}

#the maximum and minimum x the ball will be able to take after a shot
balls_to_x_boundary = {1: [-1,-1],
                    2: [-1,-1],
                    3: [-1,-1],
                    4: [-1,-1],
                    5: [-1,-1],
                    6: [-1,-1],
                    7: [-1,-1],
                    8: [-1,-1],
                    9: [-1,-1],
                    10: [-1,-1],
                    11: [-1,-1],
                    12: [-1,-1],
                    13: [-1,-1],
                    14: [-1,-1],
                    15: [-1,-1]}

#themaximum and minimum y the ball will be able to take after a shot
balls_to_y_boundary = {1: [-1,-1],
                    2: [-1,-1],
                    3: [-1,-1],
                    4: [-1,-1],
                    5: [-1,-1],
                    6: [-1,-1],
                    7: [-1,-1],
                    8: [-1,-1],
                    9: [-1,-1],
                    10: [-1,-1],
                    11: [-1,-1],
                    12: [-1,-1],
                    13: [-1,-1],
                    14: [-1,-1],
                    15: [-1,-1]}
# the chosen pocket for each ball
pocket_for_each_ball = [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1]


#A list of pockets with each element being an x-y coordinate for the pocket
pockets = [[100,300],[500,300],[900,300],[900,700],[500,700],[100,700]]


#A list of X and Y coordinates for each ball
listX = [650,700,400,110,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1]
listY = [500,350,400,320,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1]



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
        print("Pocket Chosen for this ball = {pocket}".format(pocket = pocket_for_each_ball[i-1]))
        print("-------------------------------------------------")





#brief: Finds the distance of each ball to each pocket and stores it in the dictionary 
def find_distance_to_all_pockets():
    for i in range(FIRST_BALL,NUMBER_OF_BALLS):
        if(listX[i]<0): continue
        shot_params = ball_to_shots.get(i)
        pocket_idx = 0
        for pocket in pockets:
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
            shot_params[FIRST_SLOPE] = np.nan
            shot_params[FIRST_INTERCEPT] = np.nan
        return
    for target_ball in range(FIRST_BALL,NUMBER_OF_BALLS):
        #check if ball has been potted
        if(listX[target_ball]<0 or listY[target_ball]<0): 
            shot_params = ball_to_shots.get(target_ball)
            shot_params[FIRST_SLOPE] = np.nan
            shot_params[FIRST_INTERCEPT] = np.nan
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
            if (listX[target_ball]==listX[CUE_BALL]): slope = np.inf
            else: slope = (listY[target_ball]-listY[CUE_BALL])/(listX[target_ball]-listX[CUE_BALL])
            if (slope == np.inf): intercept = np.inf
            else: intercept = listY[target_ball] - (slope * listX[target_ball])
        #shot is not possible cause collision 
        else:
            slope = np.nan
            intercept = np.nan
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
                shot_params[SECOND_SLOPES][pocket] = np.nan
                shot_params[SECOND_INTERCEPT][pocket] = np.nan
            continue
        if(math.isnan(shot_params[FIRST_INTERCEPT])):
            for pocket in range(NO_POCKETS):
                shot_params[SECOND_SLOPES][pocket] = np.nan
                shot_params[SECOND_INTERCEPT][pocket] = np.nan
            continue
        #create a line for each pocket
        pocket_index = 0;
        for pocket in pockets:
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
                if (listX[target_ball] == pocket[POCKETX]): slope = np.inf
                else: slope = (pocket[POCKETY] - listY[target_ball])/(pocket[POCKETX] - listX[target_ball])
                if (slope == np.inf): intercept = np.inf
                else: intercept = pocket[POCKETY] - (slope * pocket[POCKETX])
                shot_params[SECOND_SLOPES][pocket_index] = slope
                shot_params[SECOND_INTERCEPT][pocket_index] = intercept
            # a successful shot canot be made to that pocket
            else:
                shot_params[SECOND_SLOPES][pocket_index] = np.nan
                shot_params[SECOND_INTERCEPT][pocket_index] = np.nan
            pocket_index+=1

#brief: Draws the image that is going to be projected onto the pool table
def drawImage():
    img = np.zeros((1000,1000,3), np.uint8)
    cv.rectangle (img,(100,300),(900,700),GREEN,1)
    for target_ball in range(NUMBER_OF_BALLS):
        if listX[target_ball]>0:
            if (target_ball==CUE_BALL):
                cv.circle(img,(listX[target_ball],listY[target_ball]),RADIUS_BALL*2,WHITE,3)
            else:
                cv.circle(img,(listX[target_ball],listY[target_ball]),RADIUS_BALL*2,YELLOW,3)
    for pocket in pockets:
        cv.circle(img,(pocket[0],pocket[1]),RADIUS_POCKET*2,BLUE,6)   
    
    i = 0
    for target_ball in range(FIRST_BALL,NUMBER_OF_BALLS):
        shot_params = ball_to_shots.get(target_ball)
        if(not math.isnan(shot_params[FIRST_SLOPE])):
            cv.line(img,(listX[CUE_BALL],listY[CUE_BALL]),(listX[target_ball],listY[target_ball]),(0,0,255 - (i*10)),2);
        if((not math.isnan(pocket_for_each_ball[target_ball-1])) and pocket_for_each_ball[target_ball-1]>=0):
            pocketX = pockets[pocket_for_each_ball[target_ball-1]][POCKETX]
            pocketY = pockets[pocket_for_each_ball[target_ball-1]][POCKETY]
            cv.line(img,(listX[target_ball],listY[target_ball]),(pocketX,pocketY),(0,0,255 - (i*20)),2);
        
    cv.imwrite('img.jpeg',img)


def find_edges():
    if(listX[CUE_BALL]<0 or listY[CUE_BALL]<0): return
    for target_ball in range(FIRST_BALL,NUMBER_OF_BALLS):
        if(listX[target_ball]<0 or listY[target_ball]<0): continue
        shot_params=ball_to_shots.get(target_ball)
        if(math.isnan(shot_params[FIRST_SLOPE])):
            shot_max[POCKETX] = np.nan
            shot_max[POCKETY] = np.nan
            shot_min[POCKETX] = np.nan
            shot_min[POCKETY] = np.nan
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
        if(listX[target_ball]<0 or listY[target_ball]<0): continue
        shot_params=ball_to_shots.get(target_ball)
        x_bounds = balls_to_x_boundary.get(target_ball)
        y_bounds = balls_to_y_boundary.get(target_ball)
        if(listX[CUE_BALL] == listX[target_ball]):
            pocket_idx = 0
            for pocket in pockets: 
                if(pocket[POCKETY]<listY[target_ball] and listY[CUE_BALL]<listY[target_ball]):
                    shot_params[DISTANCES][pocket_idx] = np.nan
                    shot_params[SECOND_SLOPES][pocket_idx] = np.nan
                    shot_params[SECOND_INTERCEPT][pocket_idx] = np.nan
                elif(pocket[POCKETY]>listY[target_ball] and listY[CUE_BALL]>listY[target_ball]):
                    shot_params[DISTANCES][pocket_idx] = np.nan
                    shot_params[SECOND_SLOPES][pocket_idx] = np.nan
                    shot_params[SECOND_INTERCEPT][pocket_idx] = np.nan
                pocket_idx+=1
        elif(listX[CUE_BALL]<listX[target_ball]):
            pocket_idx = 0
            for pocket in pockets: 
                if (pocket_idx<3):
                    if(pocket[POCKETX]<x_bounds[0]):
                        shot_params[DISTANCES][pocket_idx] = np.nan
                        shot_params[SECOND_SLOPES][pocket_idx] = np.nan
                        shot_params[SECOND_INTERCEPT][pocket_idx] = np.nan
                else:
                    if(pocket[POCKETX]<x_bounds[1]):
                        shot_params[DISTANCES][pocket_idx] = np.nan
                        shot_params[SECOND_SLOPES][pocket_idx] = np.nan
                        shot_params[SECOND_INTERCEPT][pocket_idx] = np.nan
                pocket_idx+=1
        elif(listX[CUE_BALL]>listX[target_ball]):
            pocket_idx = 0
            for pocket in pockets:
                if (pocket_idx<3):
                    if(pocket[POCKETX]>x_bounds[0]):
                        shot_params[DISTANCES][pocket_idx] = np.nan
                        shot_params[SECOND_SLOPES][pocket_idx] = np.nan
                        shot_params[SECOND_INTERCEPT][pocket_idx] = np.nan
                else:
                    if(pocket[POCKETX]>x_bounds[1]):
                        shot_params[DISTANCES][pocket_idx] = np.nan
                        shot_params[SECOND_SLOPES][pocket_idx] = np.nan
                        shot_params[SECOND_INTERCEPT][pocket_idx] = np.nan
                pocket_idx+=1
            
        if(listY[CUE_BALL]==listY[target_ball]):
            pocket_idx = 0
            for pocket in pockets: 
                if(pocket[POCKETX]<listX[target_ball] and listX[CUE_BALL]<listX[target_ball]):
                    shot_params[DISTANCES][pocket_idx] = np.nan
                    shot_params[SECOND_SLOPES][pocket_idx] = np.nan
                    shot_params[SECOND_INTERCEPT][pocket_idx] = np.nan
                elif(pocket[POCKETX]>listX[target_ball] and listX[CUE_BALL]>listX[target_ball]):
                    shot_params[DISTANCES][pocket_idx] = np.nan
                    shot_params[SECOND_SLOPES][pocket_idx] = np.nan
                    shot_params[SECOND_INTERCEPT][pocket_idx] = np.nan
                pocket_idx+=1
        elif (listY[CUE_BALL] > listY[target_ball]):
            pocket_idx = 0
            for pocket in pockets:
                if (pocket_idx<3):
                    if(pocket[POCKETY]>y_bounds[0]):
                        shot_params[DISTANCES][pocket_idx] = np.nan
                        shot_params[SECOND_SLOPES][pocket_idx] = np.nan
                        shot_params[SECOND_INTERCEPT][pocket_idx] = np.nan
                else:
                    if(pocket[POCKETY]>y_bounds[1]):
                        shot_params[DISTANCES][pocket_idx] = np.nan
                        shot_params[SECOND_SLOPES][pocket_idx] = np.nan
                        shot_params[SECOND_INTERCEPT][pocket_idx] = np.nan
                pocket_idx+=1
        elif (listY[CUE_BALL] < listY[target_ball]):
            pocket_idx = 0
            for pocket in pockets:
                if (pocket_idx<3):
                    if(pocket[POCKETY]<y_bounds[0]):
                        shot_params[DISTANCES][pocket_idx] = np.nan
                        shot_params[SECOND_SLOPES][pocket_idx] = np.nan
                        shot_params[SECOND_INTERCEPT][pocket_idx] = np.nan
                else:
                    if(pocket[POCKETY]<y_bounds[1]):
                        shot_params[DISTANCES][pocket_idx] = np.nan
                        shot_params[SECOND_SLOPES][pocket_idx] = np.nan
                        shot_params[SECOND_INTERCEPT][pocket_idx] = np.nan
                pocket_idx+=1
           
            
        

def chose_pocket():
    if(listX[CUE_BALL]<0 or listY[CUE_BALL]<0): return
    for target_ball in range(FIRST_BALL, NUMBER_OF_BALLS):
        if(listX[target_ball]<0 or listY[target_ball]<0): continue
        shot_params=ball_to_shots.get(target_ball)
        if(math.isnan(shot_params[FIRST_SLOPE])): continue
        second_slopes = shot_params[SECOND_SLOPES]
        first_slope = shot_params[FIRST_SLOPE]
        distances = shot_params[DISTANCES]
        hardness_all_shots = [np.nan,np.nan,np.nan,np.nan,np.nan,np.nan]
        viable = False
        for idx in range(NO_POCKETS):
            if(math.isnan(second_slopes[idx])): continue
            if(math.isnan(distances[idx])): continue
            viable = True
            calc_dist = distances[idx] * 0.5
            calc_slope_delta = abs(second_slopes[idx] - first_slope) * 0.3
            total_hardness = calc_dist * calc_slope_delta
            hardness_all_shots[idx] = total_hardness
        #shot can be made chose best
        #print("For Ball {no}, shot is viable = {s}".format(no = target_ball,s = viable))
        #print("Hardness for each shot is = {hard}".format(hard = hardness_all_shots))
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
            pocket_for_each_ball[target_ball-1] = chosen_idx
        else: pocket_for_each_ball[target_ball-1] = np.nan
    print('Pockets For Each Ball Are = {list}'.format(list = pocket_for_each_ball))



find_distance_to_all_pockets();
create_first_lines();
create_second_lines();
find_edges();
remove_impossible_pockets();
chose_pocket();
print_dimensions();
drawImage();