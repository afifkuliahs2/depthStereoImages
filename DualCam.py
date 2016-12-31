from collections import deque
import numpy as np
import cv2

class DualCam:
    def __init__(self):
        self.cam1 = cv2.VideoCapture(0)
        self.cam2 = cv2.VideoCapture(1)


    def colorDefinition(self):
        buffersize = 64
        self.greenLower = (29, 86, 6)
        self.greenUpper = (64, 255, 255)
        self.pts = deque(maxlen=buffersize)

        self.focalLength = 50
        self.distance = 100

    def makeMask(self, colorMap, rangeLower, rangeUpper, iterationNumber):
        mask = cv2.inRange(colorMap, rangeLower, rangeUpper)
        mask = cv2.erode(mask, None, iterations=iterationNumber)
        mask = cv2.dilate(mask, None, iterations=iterationNumber)

        return mask;

    def getCenter(self, contours):
        c = max(contours, key=cv2.contourArea)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

        return center

    def getDepth(self, c1, c2, init1, init2):
        # p1 and p2 are points on camera 1, p1 is point on center projection, p2 is point on projection plane
        # p3 adn p4 are points on camera 1, p3 is point on center projection, p4 is point on projection plane
        # z = focal length / depth
        center1 = 0
        center2 = 0
        d_width = self.cam1.get(3) / 2
        p1 = {'z1': 0, 'x1': 0}
        p2 = {'z2': 0, 'x2': 0}
        p3 = {'z3': 0, 'x3': 0}
        p4 = {'z4': 0, 'x4': 0}

        if len(c1) > 0 and len(c2) > 0:
            init1 = self.getCenter(c1)
            init2 = self.getCenter(c2)
            center1 = init1[0]
            center2 = init2[0]

        p1['x1'] = d_width  # z1 still 0
        p2['x2'] = center1
        p2['z2'] = self.focalLength
        p3['x3'] = d_width + self.distance  # z3 still 0
        p4['z4'] = center2 + self.distance
        p4['x4'] = self.focalLength

        A1 = p2['x2'] - p1['x1']
        B1 = p1['z1'] - p2['z2']
        C1 = A1 * p1['z1'] + B1 * p1['x1']
        A2 = p4['x4'] - p3['x3']
        B2 = p3['z3'] - p4['z4']
        C2 = A2 * p3['z3'] - B2 * p3['x3']
        divider = A1 * B2 - A2 * B1  # Value of C1 and C2 is same !

        z = ((B2 * C1) - (B1 * C2)) / divider  # return z
        # x = ((A1 * C2) - (A2 * C1)) / divider  # return x

        return z

    def makeConture(self, contours, center, depth, frame):
        if len(contours) > 0:
            # find the largest contour in the mask, then use
            # it to compute the minimum enclosing circle and
            # centroid
            c = max(contours, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            center = self.getCenter(contours)
            font = cv2.FONT_HERSHEY_SIMPLEX

            # only proceed if the radius meets a minimum size
            if radius > 10:
                # draw the circle and centroid on the frame,
                # then update the list of tracked points
                cv2.circle(frame, (int(x), int(y)), int(radius),
                           (0, 255, 255), 2)
                cv2.circle(frame, center, 5, (0, 0, 255), -1) #draw centroid
                cv2.putText(frame, str(depth), (int(x), int(y)), font, 2, (255, 255, 255), 2, cv2.LINE_AA)

        self.pts.appendleft(center)
        return

    def showImage(self):
        ret, frame = self.cam1.read()
        ret2, frame2 = self.cam2.read();

        img1 = cv2.flip(frame, 1)
        img2 = cv2.flip(frame2, 2)

        hsvColor = cv2.cvtColor(img1, cv2.COLOR_BGR2HSV)
        hsvColor2 = cv2.cvtColor(img2, cv2.COLOR_BGR2HSV)

        mask = self.makeMask(hsvColor, self.greenLower, self.greenUpper, 2)
        mask2 = self.makeMask(hsvColor2, self.greenLower, self.greenUpper, 2)

        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
        cnts2 = cv2.findContours(mask2.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
        center = None
        center2 = None

        init1 = None
        init2 = None
        z = self.getDepth(cnts, cnts2, init1, init2)
        # print(z)

        self.makeConture(cnts, center, z, img1)
        self.makeConture(cnts2, center2, z, img2)


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
