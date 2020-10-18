import cv2
import numpy as np
from matplotlib import pyplot as plt
import random
from PIL import Image
from copy import copy
from datetime import datetime
import shutil

sigma = 500 # standard deviation used to generate end point of line

for imgNum in range(1, 159):
    startTime = datetime.now().strftime("%H:%M:%S")
    print("Started", imgNum, "at:", startTime)
    
    # Import image
    pathImg = "inputImg/0" + str(imgNum) + ".PNG"
    im = cv2.imread(pathImg) # reads an image in the BGR format
    im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)   # BGR -> RGB
    height, width, unknown = im.shape
    print(pathImg)
    
    # Import .txt
    pathTxt = "inputTxt/0" + str(imgNum) + ".txt"

    for i in range(1, 21):
        imTemp = copy(im) # Start from blank image each time

        lnWidth = random.randint(1,3) # Generate random width between 1 and 3, inclusive

        # Randomly generate line start point
        startX = random.randint(0, width)
        startY = random.randint(0, height)
        start = (startX, startY)
        print("  Start:", start)

        # Generate end points from normal distribution centered around the starting point
        endX = int(round(np.random.normal(start[0], sigma)))
        endY = int(round(np.random.normal(start[1], sigma)))

        # If numbers are outside of image, set to max/min dimension
        if endX < 0:
            endX = 0
        elif endX > width:
            endX = width

        if endY < 0:
            endY = 0
        elif endY > width:
            endY = width

        # Generate end tuple       
        end = (endX, endY)

        # Generate line on image
        rbg = random.randint(45, 255)
        colour = (rbg, rbg, rbg)
        cv2.line(imTemp, start, end, colour, lnWidth)
        #plt.imshow(im)
        #plt.show()

        imgSave = Image.fromarray(imTemp)
        imgSave.save("output/" + str(imgNum) + "_" + str(i) + ".PNG")
        
        # Calculate label data for YOLO
        label = "RSO"
        centreX = (startX + ((endX - startX) / 2)) / width
    
        startY #startValY = height - startY
        endY #endValY = height - endY
        
        if startY < endY:
            centreY = (startY + ((endY - startY) / 2)) / height
        else:
            centreY = (endY + ((startY - endY) / 2)) / height
        
        if startX < endX: # Prevents negative values if line is drawn right-->left instead of left-->right
            widthYOLO = ((endX - startX) / 2)
        else:
            widthYOLO = ((startX - endX) / 2)            
        
        if startY < endY: # Prevents negative values if line is drawn right-->left instead of left-->right
            heightYOLO = ((endY - startY) / 2)
        else:
            heightYOLO = ((startY - endY) / 2)
        
        # For drawing bounding box
        if startY < endY:
            topLeft = (int((centreX * width) - widthYOLO), startY)
            lowerRight = (int((centreX * width) + widthYOLO), endY)
        else:
            topLeft = (int((centreX * width) - widthYOLO), endY)
            lowerRight = (int((centreX * width) + widthYOLO), startY)
        
        # Draw bounding box around generated line
        thickness = 4
        colourBox = (248, 203, 43)
        imTempBox = cv2.rectangle(imTemp, topLeft, lowerRight, colourBox, thickness)
        
        # Draw bounding box around real lines
        with open(pathTxt, 'r') as fobj: # Get lines labels from .txt file
            allLines = [[float(num) for num in line.split()] for line in fobj]

        for k in range(0, len(allLines)): # For each real line in image
            # Get values from .txt file
            print("    k: ", k)
            centreXReal = allLines[k][1]
            centreYReal = allLines[k][2]
            widthYOLOReal = (allLines[k][3] * width) / 2
            heightYOLOReal = (allLines[k][4] * height) / 2
            
            # Calculate corners of bounding box
            topLeftReal = (int((centreXReal * width) - widthYOLOReal), int((centreYReal * height) - heightYOLOReal))
            lowerRightReal = (int((centreXReal * width) + widthYOLOReal), int((centreYReal * height) + heightYOLOReal))
            
            # Draw bounding box
            colourBox = (28, 232, 155)
            imTempBox = cv2.rectangle(imTempBox, topLeftReal, lowerRightReal, colourBox, thickness)            
        
        # Save annotated image
        imgSaveBox = Image.fromarray(imTempBox)
        imgSaveBox.save("outputBox/" + str(imgNum) + "_" + str(i) + ".PNG")
        
        # Create .txt file with labels
        pathTxtGenerated = "output/" + str(imgNum) + "_" + str(i) + ".txt"
        shutil.copy(pathTxt, pathTxtGenerated) # Create new copy of .txt file

        widthTxt = (widthYOLO * 2) / width
        heightTxt = (heightYOLO * 2) / height
        centreYTxt = 1 - centreY
        
        txtToAppend = ("0" + " " + str("%.6f" % round(centreX, 6)) + " " + str("%.6f" % round(centreY, 6))
                       + " " + str("%.6f" % round(widthTxt, 6)) + " " + str("%.6f" % round(heightTxt, 6)))
        print("   ", str(imgNum) + "_" + str(i) + ".txt = " + txtToAppend)
        
        with open(pathTxtGenerated, "a") as f:
             f.write(txtToAppend) # Append to .txt file
            
endTime = datetime.now().time().strftime("%H:%M:%S")
print('Finished:', endTime)