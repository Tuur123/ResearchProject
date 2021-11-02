from djitellopy import tello
from threading import Thread
import cv2

streaming = True

drone = tello.Tello()
drone.connect()
drone.streamon()

print(f"Battery level: {drone.get_battery()}%")



def videoStream(drone):

    while streaming:
        img = drone.get_frame_read().frame
        cv2.imshow("Stream", img)
        cv2.waitKey(1)

stream = Thread(target=videoStream(drone), daemon=True)
stream.start()

try:
    while True:
        pass

except KeyboardInterrupt:
    streaming = False
    stream.join()
    cv2.destroyAllWindows()
    print("Exiting...")
