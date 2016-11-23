from __future__ import print_function
from PIL import Image
from PIL import ImageTk
import Tkinter as tk
import threading
import imutils
import datetime
import cv2
import os

class StereoCams:
    def __init__(self, videoSource, outputPath):
        self.videoSource = videoSource
        self.outputPath = outputPath
        self.frame = None
        self.thread = None
        self.stopEvent = None

        self.root = tk.Tk()
        self.panel = None

        captureBtn = tk.Button(self.root, text="Capture Image", command=self.captureImage)
        captureBtn.pack(side="bottom", fill="both", expand="yes", padx=10, pady=10)

        self.stopEvent = threading.Event()
        self.thread = threading.Thread(target=self.captureLoop, args=())
        self.thread.start()

        self.root.wm_title("Stereo Cams")
        self.root.wm_protocol("WM_DELETE_WINDOW", self.onClose)


    def captureLoop(self):
        try:
            while not self.stopEvent.is_set():
                self.frame = self.videoSource.read()
                self.frame = imutils.resize(self.frame, 400)

                image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGBA)
                image = Image.fromarray(image)
                image = ImageTk.PhotoImage(image)

                if self.panel is None:
                    self.panel = tk.Label(image=image)
                    self.panel.image = image
                    self.panel.pack(side="left", padx=10, pady=10)

                else:
                    self.panel.configure(image=image)
                    self.panel.image = image

        except RuntimeError, e:
            print("[INFO] caught a RuntimeError")

    def captureImage(self):
        ts = datetime.datetime.now()
        filename = "{}_1.jpg".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))
        p = os.path.sep.join((self.outputPath, filename))

        cv2.imwrite(p, self.frame.copy())
        print("[INFO] saved {}".format(filename))

    def onClose(self):
        # set the stop event, cleanup the camera, and allow the rest of
        # the quit process to continue
        print("[INFO] closing...")
        self.stopEvent.set()
        self.videoSource.stop()
        self.root.quit()



