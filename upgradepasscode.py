import cv2 as cv
import numpy as np
import sys, os

###############################
###LANGUAGE DEFINED
# Any number of accepted passcodes can be added by adding a tuple in the
# format shown below to lang


lang = set()
lang.add(((0, ('center', 'center')), (5, ('low','left'))))
lang.add(((1, ('center', 'center')), (2, ('center', 'center'))))


# Evaluation function
# Called near the end to check whether the given passcode is in the language
def eval(whats, wheres):
    if tuple(zip(whats, wheres)) in lang:
        return True

    if len(whats) == 2:
        if whats[0] < whats[1]:
            return True

    return False 

# Helper function to find the biggest contour given a group of them
def findbiggest(contours):
    maxarea = 0
    maxi = 0
    for i in range (len(contours)):
        cnt = contours[i]
        area = cv.contourArea(cnt)
        if (area > maxarea):
            maxarea = area
            maxi = i
    return contours[maxi], maxi


##################
### READ INPUT ###
##################
# endinput checks for the input of end.jpg
# flag is true and algo  runs until the passcode is found in the language
endinput, flag = False, True
whats, wheres = [], []
while flag:

    f = input("Enter the image for evaluation:\n")
    while not os.path.isfile(f):
        f = input("That file could not be found. Please provide a correct path:\n")
    img = cv.imread(f)

    #delete blue, green channels, convert to grayscale, threshold
    #get binary image 
    height, width = img.shape[:2]
    img[:,:,0] = 0
    img[:,:,1] = 0
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    blur = cv.GaussianBlur(gray,(5,5),0)
    retval, threshold = cv.threshold(blur, 20, 255, cv.THRESH_BINARY)
#    s = 'binary-'+sys.argv[1]
#    cv.imwrite(s, threshold)

    #find contours and get biggest one
    _, contours, heirarchy = cv.findContours(threshold, 2, 1)
    cnt, i = findbiggest(contours)
 
    # create clean convex hull with only one point at each fingertip
    hull = cv.convexHull(cnt, returnPoints=False)

    remove = []
    for i in range(hull.shape[0]):
        for j in range(i+1, hull.shape[0]):
            d = np.linalg.norm(cnt[hull[i]][0]-cnt[hull[j]][0])
            if d < width/20:    #      horizontal pixels / 20 
                remove.append(i)
                break
    hull = np.delete(hull, remove, 0)       # new clean hull


    # find convexity defects i.e. points between fingers
    defects = cv.convexityDefects(cnt, hull)

    # fingertips is a list of lists(3) where the first value is the 
    # index for the fingertip, and the following two are the indices
    # for the neighboring defect points
    # palm is for creating a new contour containing just the hand, to 
    # later find the correct center of mass for the input
    fingertips, palm = [], []
    prevf = -1
    for i in range(defects.shape[0]):
        s, e, f, d = defects[i,0]
        if prevf > 0:
            fingertips.append([s, prevf, f])
        prevf = f
        start = tuple(cnt[s][0])
        end = tuple(cnt[e][0])
        far = tuple(cnt[f][0])
        palm.append(cnt[f][0])
        cv.line(img,far,start,[0,255,0],2)
        cv.line(img,far,end,[0,255,0],2)
        cv.circle(img,far,5,[0, 0,255],30)

    numfing = 0
    for f, n1, n2 in fingertips:
        cv.circle(img, tuple(cnt[f][0]), 5, [255, 255, 255], 30)
        v1 = cnt[f][0] - cnt[n1][0]
        v2 = cnt[f][0] - cnt[n2][0]
        theta = np.arccos(np.dot(v1, v2)/(np.linalg.norm(v1)*np.linalg.norm(v2)))
        if theta < 0.8:
            numfing += 1

#    print(numfing)
        
    if numfing < 6:
        whats.append(numfing)
    elif numfing == 8 :
        endinput = True
        flag = False
    else:
        whats.append('unknown')


#############
###WHERE#####
#############

    palmcnt = np.array([[x] for x in palm])
    #cv.drawContours(img, [cnt], 0, (0,255,0), 3)
    M = cv.moments(palmcnt)
    #print (M)

    # find center of mass of contour
    cx = int(M['m10']/M['m00'])
    cy = int(M['m01']/M['m00'])
    cv.circle(img, (cx,cy), 7, (255, 255, 255), -1)

    if cy < 2*height/5:
        v = 'up'
    elif cy < 3*height/5:
        v = 'center'
    else:
        v = 'low'
    if cx < 2*width/5:
        h = 'left'
    elif cx < 3*width/5:
        h = 'center'
    else:
        h = 'right'
    
    if not endinput:
        wheres.append((v, h))
           
#    cv.imshow('img', img)
#    cv.waitKey(0)
#    cv.destroyAllWindows()

    if eval(whats, wheres):
        print("PASS")
        flag = False

#################
###EVALUATION###
################

if endinput:
    print("FAIL!")

