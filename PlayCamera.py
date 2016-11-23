from __future__ import print_function
from StereoCam import StereoCams
from imutils.video import WebcamVideoStream
import time
import argparse

argue = argparse.ArgumentParser()
argue.add_argument("-o", "--output", required=True, help="path to output directory to store snapshots")
args = vars(argue.parse_args())

print("[INFO] warming up camera...")
cam1 = WebcamVideoStream(1).start()
time.sleep(2.0)

fun = StereoCams(cam1, args["output"])
fun.root.mainloop()