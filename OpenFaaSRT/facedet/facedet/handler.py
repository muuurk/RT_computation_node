try:
    import cv2
except:
    import cv2

import os
import sys
import numpy as np
import time


def handle(req, mmframe, imgpath):
    # Load the cascade
    face_cascade = cv2.CascadeClassifier('/dev/shm/haarcascade_frontalface_default.xml')

    # To capture video from webcam.
    #cap = cv2.VideoCapture(0)
    img = cv2.imread(imgpath)
    # To use a video file as input
    # cap = cv2.VideoCapture('filename.mp4')

    with open("log.txt", "a") as f:
        print("Recording Webcam...")
        print("-------------------------------")
        print("FPS\tAVG RUNTIME (in ns) DURING A SEC")

    frames_per_sec = 1
    pre_sec_time = 0
    sum_run_time = 0
    while True:
        start_time = time.time_ns()

        if start_time - pre_sec_time > 1000000000:
            avg_run_time = int(sum_run_time/frames_per_sec)
            with open("log.txt", "a") as f:
                f.write("{}\t{}\n".format(frames_per_sec, avg_run_time))
            pre_sec_time = start_time
            frames_per_sec = 0
            sum_run_time = 0
            frames_per_sec += 1
        else:
            frames_per_sec += 1

        # Read the frame
        #_, img = cap.read()

        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Detect the faces
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)

         # Draw the rectangle around each face
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)

        mmframe.write(img.tobytes())
        mmframe.seek(0)

        end_time = time.time_ns()

        k = cv2.waitKey(30) & 0xff
        if k==27:
            break

        sum_run_time += end_time-start_time
        os.sched_yield()
        #cap.release()
    return "ok"
