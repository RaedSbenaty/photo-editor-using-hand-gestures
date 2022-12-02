import cv2 as cv
import numpy as np


cap = cv.VideoCapture(0)

bgFrame = None 
while 1:
	_,frame = cap.read()
	k = cv.waitKey(1)
	if k == ord('z') and bgFrame == None :
		bgFrame = frame
	elif k ==ord('q'):
		break 
	if bgFrame is not None: 
		d = cv.dif(frame,bgFrame)
		cv.imshow("deff",d)
	cv.imshow("input",frame)

