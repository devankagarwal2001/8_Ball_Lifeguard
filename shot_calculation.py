import math
from array import *
import cv2 as cv
import numpy as np

radius = 1
radius_pocket = 1.5
first_lines = [[-1,-1],[-1,-1],[-1,-1],[-1,-1],[-1,-1],[-1,-1],[-1,-1],[-1,-1],[-1,-1],[-1,-1],[-1,-1],[-1,-1],[-1,-1],[-1,-1]]
second_lines = [[-1,-1],[-1,-1],[-1,-1],[-1,-1],[-1,-1],[-1,-1],[-1,-1],[-1,-1],[-1,-1],[-1,-1],[-1,-1],[-1,-1],[-1,-1],[-1,-1]]
pockets_for_each_ball = [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1]
distance_cue_pocket = [-1,-1,-1,-1,-1,-1]
cloests_pocket_for_each_ball = [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1]
#print(first_lines)
#assuming all x and y are positive and -1 would mean that the ball is not on table
#assuming the format of lists as follows:
#list_ = [cue_ball,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
#assuming the pockets are at [0,0] [0,400], [400,400], [800,400], [800,0], [400.0]
pockets = [[100,300],[500,300],[900,300],[900,700],[500,700],[100,700]]
def create_first_lines(listX,listY):
    if listX[0] == 0 or listY[0] == 0 : print("Cue Ball Pocketed")
    for i in range(1,15):
        if(listX[i]== -1 and listY[i]== -1): continue
        slope = 0
        b = -1
        diffX = listX[i]-listX[0]
        diffY = listY[i]-listY[0]
        slope = diffY/diffX
        b = listY[i] - (slope*listX[i])
        #check collisions for each ball with every other ball
        for j in range(1,15):
            #cant check with itself
            if i == j: continue
            if (listX[j] == -1 and listY[j] == -1): continue
            #increase the y coordinates with the radius of the cue ball
            first_check = lineCircle(listX[0],listY[0]+radius,listX[i],listY[i]+radius,listX[j],listY[j],radius)
            second_check = lineCircle(listX[0],listY[0]-radius,listX[i],listY[i]-radius,listX[j],listY[j],radius)
        if not (first_check or second_check):
            first_lines[i-1][0] = slope
            first_lines[i-1][1] = b
        else:
            first_lines[i-1][0] = -3
            first_lines[i-1][1] = -3
        #now check for collisions

def distance_bw_cue_ball_and_pocket():
    if(listX[0]==-1): return
    pocket_indx = 0
    for pocket in pockets:
        distanceX = (listX[0] - pocket[0]) * (listX[0] - pocket[0])
        distanceY = (listY[0] - pocket[1]) * (listY[0] - pocket[1])
        dist = math.sqrt(distanceX + distanceY)
        distance_cue_pocket[pocket_indx] = dist
        pocket_indx+=1

def closest_pocket_to_cue():
    closest_dist = 1000000
    cur_ind = 0
    min_ind = 0
    for dist in distance_cue_pocket:
        if (dist<closest_dist):
            closest_dist = dist
            min_ind = cur_ind
        cur_ind += 1
    return min_ind

#buggy
def create_second_lines(listX, listY):
    if listX[0] == 0 or listY[0] == 0 : print("Cue Ball Pocketed")
    distance_bw_cue_ball_and_pocket()
    closest_pocket =  closest_pocket_to_cue()
    for i in range(1,15):
        if (listX[i]==-1 or listY[i]==-1): continue
        #for each ball create possible shots if no collision
        all_shots_for_current_ball = [[-1,-1],[-1,-1],[-1,-1],[-1,-1],[-1,-1],[-1,-1]]
        pocket_ind = 0
        for pocket in pockets:
            diffX = pocket[0] - listX[i]
            diffY = pocket[1] - listY[i]
            slope = diffY/diffX
            b = listY[i] - (slope * listX[i])
            success = True
            if(pocket[0]>listX[0] and pocket[0]<listX[i]):
                all_shots_for_current_ball[pocket_ind][0] = 100000000
                all_shots_for_current_ball[pocket_ind][1] = 100000000
                pocket_ind+=1
                continue
            elif(pocket[0]<listX[0] and pocket[0]>listX[i]):
                all_shots_for_current_ball[pocket_ind][0] = 100000000
                all_shots_for_current_ball[pocket_ind][1] = 100000000
                pocket_ind +=1
                continue
            for j in range(15):
                if i == j: continue
                if (listX[j] == -1 and listY[j] == -1): continue
                first_check = lineCircle(listX[i],listY[i]+radius,pocket[0],pocket[1],listX[j],listY[j],radius)
                second_check = lineCircle(listX[i],listY[i]-radius,pocket[0],pocket[1],listX[j],listY[j],radius)
                if (first_check or second_check):
                    success = False
            if (success):
                    all_shots_for_current_ball[pocket_ind][0] = slope
                    all_shots_for_current_ball[pocket_ind][1] = b
            else:
                all_shots_for_current_ball[pocket_ind][0] = 100000000
                all_shots_for_current_ball[pocket_ind][1] = 100000000
            pocket_ind += 1
        #at this point all possible shots should be caculated with no collisions 
        min_delta = 100000000
        min_ind = -1
        possible_shot = False
        if (i==3):
            print("All Possible Shots")
            print(all_shots_for_current_ball)
            print("First Line for 3rd Ball")
            print(first_lines[2])
        
        for j in range(5):
            if j == closest_pocket: 
                continue
            shot = all_shots_for_current_ball[j]
            if(shot[0] == 100000000): continue
            possible_shot = True
            slope_delta = abs(shot[0] - first_lines[i-1][0])
            if(slope_delta<min_delta):
                min_delta = slope_delta
                min_ind = j
        
        if (possible_shot):
            if(first_lines[i-1][0] != -3):
                second_lines[i-1][0] = all_shots_for_current_ball[min_ind][0]
                second_lines[i-1][1] = all_shots_for_current_ball[min_ind][1]
                pockets_for_each_ball[i-1] = min_ind
            else:
                second_lines[i-1][0] = -3
                second_lines[i-1][1] = -3
        else:
            second_lines[i-1][0] = -3
            second_lines[i-1][1] = -3

                    

        




#taken from: https://www.jeffreythompson.org/collision-detection/line-circle.php

# Definition: Checks if the line given bt (x0,y0) and (x1,y1) lies on the circle given by (cx,cy) and radius
# Return Value: True if the line interesects at one point or two, False if not
# Errors: NA
def lineCircle(x1,y1,x2,y2,cx,cy,r):

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
    
    
def drawImage():    
    img = np.zeros((1000,1000,3), np.uint8)
    cv.rectangle (img,(100,300),(900,700),(0,255,0),1)
    for i in range(15):
        if listX[i]!=-1:
            if (i==0):
                cv.circle(img,(listX[i],listY[i]),radius,(255,255,255),3)
            else:
                cv.circle(img,(listX[i],listY[i]),radius,(0,255,255),3)
    for pocket in pockets:
        cv.circle(img,(pocket[0],pocket[1]),radius*3,(255,0,0),3)   
    create_first_lines(listX,listY)
    print(first_lines)
    create_second_lines(listX,listY)
    for i in range(1,15):
        if ((listX[i]!=-1) and (first_lines[i-1]!=-3)):
            cv.line(img,(listX[0],listY[0]),(listX[i],listY[i]),(0,0,255),2);
    for i in range(1,15):
        if ((listX[i]!=-1) and (pockets_for_each_ball[i-1]!=-1)):
            pocketX = pockets[pockets_for_each_ball[i-1]][0]
            pocketY = pockets[pockets_for_each_ball[i-1]][1]
            cv.line(img,(listX[i],listY[i]),(pocketX,pocketY),(0,0,255),2);

    cv.imwrite('img.jpg',img)

listX = [108,130,150,800,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1]
listY = [308,350,350,500,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1]
drawImage();
