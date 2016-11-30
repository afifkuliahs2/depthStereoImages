from collections import deque
import numpy as np
import cv2

class DualCam:
    def __init__(self):
        self.cam1 = cv2.VideoCapture(0)
        self.cam2 = cv2.VideoCapture(1)


    def colorDefinition(self):
        buffersize = 64
        self.greenLower = (29,86,6)
        self.greenUpper = (64,255,255)
        self.pts = deque(maxlen=buffersize)

    def makeMask(self, colorMap, rangeLower, rangeUpper, iterationNumber):
        mask = cv2.inRange(colorMap, rangeLower, rangeUpper)
        mask = cv2.erode(mask, None, iterations=iterationNumber)
        mask = cv2.dilate(mask, None, iterations=iterationNumber)

        return mask;

    def makeConture(self, contours, center, frame):
        if len(contours) > 0:
            # find the largest contour in the mask, then use
            # it to compute the minimum enclosing circle and
            # centroid
            c = max(contours, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

            # only proceed if the radius meets a minimum size
            if radius > 10:
                # draw the circle and centroid on the frame,
                # then update the list of tracked points
                cv2.circle(frame, (int(x), int(y)), int(radius),
                           (0, 255, 255), 2)
                cv2.circle(frame, None, 5, (0, 0, 255), -1)

        self.pts.appendleft(center)
        return

    def showImage(self):
        ret, frame = self.cam1.read()
        ret2, frame2 = self.cam2.read();

        img1 = cv2.flip(frame,1)
        img2 = cv2.flip(frame2,2)


        # bisa jadi method
        hsvColor = cv2.cvtColor(img1, cv2.COLOR_BGR2HSV)
        hsvColor2 = cv2.cvtColor(img2, cv2.COLOR_BGR2HSV)

        mask = self.makeMask(hsvColor, self.greenLower, self.greenUpper, 2)
        mask2 = self.makeMask(hsvColor2, self.greenLower, self.greenUpper, 2)

        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
        cnts2 = cv2.findContours(mask2.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
        center = None
        center2 = None

        self.makeConture(cnts, center, img1)
        self.makeConture(cnts2, center2, img2)

        cv2.imshow('Camera 1', img1)
        cv2.imshow('Camera 2', img2)

    def closeAll(self):
        self.cam1.release()
        self.cam2.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    dualCam = DualCam()

    while(True):
        dualCam.colorDefinition()
        dualCam.showImage()
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    dualCam.closeAll()