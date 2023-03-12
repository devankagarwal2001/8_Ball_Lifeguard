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
radius = 0.02
first_lines = [[-1]*2]*14
#assuming all x and y are positive and -1 would mean that the ball is not on table
#assuming the format of lists as follows:
#list_ = [cue,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
def create_first_lines(listX,listY):
    if listX[0] == -1 or listY[0] == -1 : printf("Cue Ball Pocketed")
    for i in range(1,15):
        slope = 0
        b = -1
        diffX = listX[i]-listX[0]
        diffY = listY[i]-listY[0]
        slope = diffX/diffY
        b = listY[i] - (slope*listX[i])
        #at this point we have the line
        #for each line, there will be two corresponding lines showing the balls movement
        #these two lines are going to be y = mx + b - radius_cue
        # and y = mx + b + radius_cue
        # we need to remove the lines where we see a collision occur
        for j in range(1,15):
            #cant check with itself
            if i == j: continue
            first_check = check_collisions(slope,b+radius,listX[i],listY[i],radius)
            second_check = check_collisions(slope,b-radius,listX[i],listY[i],radius)
        if not (first_check or second_check):
            first_lines[i-1][0] = slope
            first_lines[i-1][1] = b
        else:
            first_lines[i-1][0] = 0
            first_lines[i-1][1] = 0
            print(first_lines[i-1])
        #now check for collisions


#buggy
def check_collisions(slope,b,cX,cY,radius):
    # y = mx + b
    #y - mx - b = 0
    dist = abs((-1*slope*cX) + cY + (-1*b)) / math.sqrt((slope*slope) + 1)
    print(dist)
    print(radius)
    if(radius>=dist): return True
    else: return False

listX = [13,91,21,30,85,76,43,51,79,6,13,87,49,32,60]
listY = [19,51,91,66,55,28,76,53,42,84,18,49,44,89,11]
create_first_lines(listX,listY)

