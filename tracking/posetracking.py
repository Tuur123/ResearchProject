from eval.savedata import FrameSaver
from djitellopy import tello
from threading import Thread
from simple_pid import PID
import mediapipe as mp
import math
import time
import cv2

flying_enabled = False

# init frame saver
saver = FrameSaver("eval/frames/frames.pkl")

# init drone
drone = tello.Tello()
drone.connect()
drone.streamon()

# check battery
print(f"Battery level: {drone.get_battery()}%")

# constants
img_h, img_w = 720, 960
set_point_x = img_w // 2
set_point_y = img_h // 2
set_point_z = (img_w * img_h) // 16 # keep face in 1/16th of frame

# detector
poseDetector = mp.solutions.pose.Pose(min_detection_confidence=0.8, min_tracking_confidence=0.8)
 
# mp drawing
mpDraw = mp.solutions.drawing_utils

# PIDs
pid_x = PID(-0.15, -0.7, -0.1, setpoint=set_point_x, sample_time = 0.01)
pid_y = PID(-0.2, -0.2, 0, setpoint=set_point_y, sample_time = 0.01)
pid_z = PID(1, 0.1, 0.1, setpoint=set_point_z, sample_time = 0.01)

pid_x.output_limits = (-100, 100)
pid_y.output_limits = (-100, 100)
pid_z.output_limits = (-100, 100)

# CV functions
def findPose(img):

    results = poseDetector.process(img)
    landmarks = results.pose_landmarks

    if landmarks:
        img, speeds, errors = trackPose(img, landmarks.landmark)
        return img, speeds, errors
    else:
        return img, None, None
   
def trackPose(img, landmark): 

    # face average
    face = {'x': landmark[0].x * img_w,
            'y': landmark[0].y * img_h,
            'z': landmark[0].z * img_w}

    # draw face average
    img = cv2.circle(img, (set_point_x, set_point_y), 5, (255, 0, 0), cv2.FILLED) # setpoint
    img = cv2.circle(img, (int(face['x']), int(face['y'])), 5, (0, 0, 255), cv2.FILLED) # face location
    img = cv2.line(img, (set_point_x, set_point_y), (int(face['x']), int(face['y'])), (255, 0, 0), 2, cv2.FILLED)
    
    # draw error tolerance
    img = cv2.line(img, ((set_point_x - 50), set_point_y), ((set_point_x + 50), set_point_y), (0, 255, 0), 2, cv2.FILLED) # x
    img = cv2.line(img, (set_point_x, (set_point_y - 50)), (set_point_x, (set_point_y + 50)), (0, 255, 0), 2, cv2.FILLED) # y

    # calc errors
    errors = (abs(face['x'] - set_point_x), abs(face['y'] - set_point_y), abs(face['z'] - set_point_z))

    # calc speeds
    speeds = [int(pid_x(face['x'])), int(pid_y(face['y'])), -int(pid_z(face['z']))]

    # keep pid loop from oscillating


    return img, speeds, errors


# start drone
if flying_enabled:

    def fly(drone):
        time.sleep(2) # wait until video stream start before takeoff
        drone.takeoff()

    Thread(target=fly, args=(drone,), name="Takeoff Thread").start()

try:
    while True:

        pTime = time.time()
        img, speeds, errors = findPose(drone.get_frame_read().frame)

        if speeds:     

            if flying_enabled:
                drone.send_rc_control(0, 0, 0, speeds[0])
           
            saver.saveFrame(img, speeds, errors)
            print(f"Speeds: {speeds}")

        else:
            if flying_enabled:
                drone.send_rc_control(0, 0, 0, 0)
        try:
            fps = int(1 / (time.time() - pTime))
        except ZeroDivisionError:
            fps = "999+"

        cv2.putText(img, f"{fps} fps", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 1)

        cv2.imshow("Stream", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            if flying_enabled:
                drone.land()  
            running = False
            cv2.destroyAllWindows()
            break

except KeyboardInterrupt:
    if flying_enabled:
        drone.land()
    running = False
    cv2.destroyAllWindows()