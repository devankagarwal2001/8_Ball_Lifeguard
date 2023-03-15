import math
from array import *
radius = 1
first_lines = [[-1,-1],[-1,-1],[-1,-1],[-1,-1],[-1,-1],[-1,-1],[-1,-1],[-1,-1],[-1,-1],[-1,-1],[-1,-1],[-1,-1],[-1,-1],[-1,-1]]
#print(first_lines)
#assuming all x and y are positive and -1 would mean that the ball is not on table
#assuming the format of lists as follows:
#list_ = [cue_ball,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
def create_first_lines(listX,listY):
    if listX[0] == -1 or listY[0] == -1 : printf("Cue Ball Pocketed")
    for i in range(1,15):
        if(listX[i]== -1 and listY[i]== -1): continue
        slope = 0
        b = -1
        diffX = listX[i]-listX[0]
        diffY = listY[i]-listY[0]
        slope = diffX/diffY
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
    print(first_lines)
        #now check for collisions


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
    
    


listX = [1,30,50,99,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1]
listY = [1,50,50,100,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1]
create_first_lines(listX,listY)
#print(first_lines)

