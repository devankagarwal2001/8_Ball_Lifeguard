//@TODO: Figure out how to read input from Jimmys CV Systems
//@TODO: Once given a system of points/balls,
//@TODO: Seperate shots out into solids and stripes
//@TODO: Once we have solids or stripes, for selected category:
    1. Calculate distance from cue ball
    2. Calculate distance from each pocket 
    3. Calculate angle of hit required 
    4. Check if any bounces need to be made
    5. Do this for all 6 pockets. Discount shots where a different colored ball interfers
    6. Find minimum hardness from each pocket. 
    7. Store this value in an array (15 ints one for each ball)
    8. find the minimum of this array for the selectod category.
//@TODO: Once we have the ball calculated, we tell the projector to display this:
    1. Make an image of cue stick, lines and selected pocket.
    2. Send an image to projector. 
