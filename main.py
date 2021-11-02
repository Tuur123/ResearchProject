from djitellopy import tello
from threading import thread
import cv2

tello = tello.Tello()

tello.connect()
tello.streamon()

def displaySteam(tello):
    img = tello.get_frame_read().frame
    cv2.imshow("Stream", img)
    cv2.waitkey(1)

