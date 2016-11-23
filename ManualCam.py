import numpy as np
import cv2

cap = cv2.VideoCapture(0)
cap2 = cv2.VideoCapture(1)

while(True):
    ret, frame = cap.read()
    ret2, frame2 = cap2.read()

    image = cv2.flip(frame, 1)
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    image2 = cv2.flip(frame2, 1)
    image2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

    cv2.imshow('frame', image)
    cv2.imshow('frame2', image2)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()