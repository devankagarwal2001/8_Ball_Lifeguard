#TODO: Figure out how to read input from Jimmys CV Systems
#TODO: Once given a system of points/balls,
#TODO: Seperate shots out into solids and stripes
#TODO: Once we have solids or stripes, for selected category:
    # 1. Calculate distance from cue ball
    # 2. Calculate distance from each pocket 
    # 3. Calculate angle of hit required 
    # 4. Check if any bounces need to be made
    # 5. Do this for all 6 pockets. Discount shots where a different colored ball interfers
    # 6. Find minimum hardness from each pocket. 
    # 7. Store this value in an array (15 ints one for each ball)
    # 8. find the minimum of this array for the selectod category.
#TODO: Once we have the ball calculated, we tell the projector to display this:
    # 1. Make an image of cue stick, lines and selected pocket.
    # 2. Send an image to projector. 

import math
from array import *
radius = 0.02
first_lines = [[-1,-1],[-1,-1],[-1,-1],[-1,-1],[-1,-1],[-1,-1],[-1,-1],[-1,-1],[-1,-1],[-1,-1],[-1,-1],[-1,-1],[-1,-1],[-1,-1]]
#print(first_lines)
#assuming all x and y are positive and -1 would mean that the ball is not on table
#assuming the format of lists as follows:
#list_ = [cue_ball,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
def create_first_lines(listX,listY):
    if listX[0] == -1 or listY[0] == -1 : printf("Cue Ball Pocketed")
    for i in range(1,15):
        slope = 0
        b = -1
        diffX = listX[i]-listX[0]
        diffY = listY[i]-listY[0]
        slope = diffX/diffY
        b = listY[i] - (slope*listX[i])
        #check collisions for each ball with every other ball
        for j in range(1,15):
            #cant check with itself
            if i == j: continue\
            #increase the y coordinates with the radius of the cue ball
            first_check = check_collisions(listX[0],listY[0]+radius,listX[i],listY[i]+radius,listX[j],listY[j],radius)
            first_check = check_collisions(listX[0],listY[0]-radius,listX[i],listY[i]-radius,listX[j],listY[j],radius)
        if not (first_check or second_check):
            first_lines[i-1][0] = slope
            first_lines[i-1][1] = b
        else:
            first_lines[i-1][0] = 0
            first_lines[i-1][1] = 0
    print(first_lines)
        #now check for collisions


#buggy

# Definition: Checks if the line given bt (x0,y0) and (x1,y1) lies on the circle given by (cx,cy) and radius
# Return Value: True if the line interesects at one point or two, False if not
# Errors: NA
def check_collisions(x0,y0,x1,y1,cX,cY,radius):
    distX = x0 - x1
    disty = y0 - y1
    line_len = math.sqrt((distX*distX) + (distY*distY))
    #after we have length, we get dot profuct of line and circle
    dot = (((cx-x1)*(x2-x1)) + ((cy-y1)*(y2-y1)))/pow(line_len,2)
    closestX = x1 + (dot * (x2-x1))
    closestY = y1 + (dot * (y2-y1))
    


listX = [13,91,21,30,85,76,43,51,79,6,13,87,49,32,60]
listY = [19,51,91,66,55,28,76,53,42,84,18,49,44,89,11]
create_first_lines(listX,listY)
#print(first_lines)

