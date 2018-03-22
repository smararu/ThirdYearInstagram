import cv2
import numpy as np
import sys

# Get user supplied values
imagePath = sys.argv[1]

faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
eyeCascade = cv2.CascadeClassifier('haarcascade_eye.xml')

# cascPath = "haarcascade_frontalface_default.xml"

# # Create the haar cascade
# faceCascade = cv2.CascadeClassifier(cascPath)

# Read the image
image = cv2.imread(imagePath)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Detect faces in the image
faces = faceCascade.detectMultiScale(gray, 1.3, 5)

for (x,y,w,h) in faces:
    image = cv2.rectangle(image,(x,y),(x+w,y+h),(255,0,0),2)
    roiGray = gray[y:y+h,x:x+w]
    roiColor = image[y:y+h,x:x+w]
    eyes = eyeCascade.detectMultiScale(roiGray)
    for (ex,ey,ew,eh) in eyes:
        cv2.rectangle(roiColor,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)


# # Detect faces in the image
# faces = faceCascade.detectMultiScale(
#     gray,
#     scaleFactor=1.1,
#     minNeighbors=5,
#     minSize=(30, 30)
#     # flags = cv2.CV_HAAR_SCALE_IMAGE
# )

print("Found {0} faces!".format(len(faces)))

# # Draw a rectangle around the faces
# for (x, y, w, h) in faces:
#     cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)

cv2.imshow("Faces found", image)
cv2.waitKey(0)
cv2.destroyAllWindows()
