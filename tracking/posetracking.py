from djitellopy import tello
from simple_pid import PID
import mediapipe as mp
import numpy as np
import time
import cv2

flying_enabled = True

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
set_point_z = (img_w * img_h) // 12

# detector
poseDetector = mp.solutions.pose.Pose(min_detection_confidence=0.8, min_tracking_confidence=0.8)
 
# mp drawing
mpDraw = mp.solutions.drawing_utils

# PIDs
pid_x = PID(-0.2, 0, -0.0, setpoint=set_point_x, sample_time = None)
pid_y = PID(1, 0.1, 0.1, setpoint=set_point_y, sample_time = None)
pid_z = PID(1, 0.1, 0.1, setpoint=set_point_z, sample_time = None)
pid_x.proportional_on_measurement = True


pid_x.output_limits = (-100, 100)
pid_y.output_limits = (-100, 100)
pid_z.output_limits = (-100, 100)


def findPose(img):

    results = poseDetector.process(img)
    landmarks = results.pose_landmarks

    if landmarks:
        img, speeds = trackPose(img, landmarks)
        return img, speeds
    else:
        return img, None
   
def trackPose(img, landmarks): 

    # left eye
    left_eye_x = landmarks.landmark[2].x
    left_eye_y = landmarks.landmark[2].y
    left_eye_z = landmarks.landmark[2].z

    # right eye
    right_eye_x = landmarks.landmark[5].x
    right_eye_y = landmarks.landmark[5].y
    right_eye_z = landmarks.landmark[5].z

    # nose
    nose_x = landmarks.landmark[0].x
    nose_y = landmarks.landmark[0].y
    nose_z = landmarks.landmark[0].z

    face_x = (left_eye_x + right_eye_x + nose_x) / 3
    face_y = (left_eye_y + right_eye_y + nose_y) / 3
    face_z = (left_eye_z + right_eye_z + nose_z) / 3

    # face average
    face = {'x': face_x * img_w, 'y': face_y * img_h, 'z': face_z * img_w}

        # draw face average
    img = cv2.circle(img, (int(face['x']), int(face['y'])), 5, (0, 0, 255), cv2.FILLED)
    img = cv2.circle(img, (set_point_x, set_point_y), 5, (255, 0, 0), cv2.FILLED)
    img = cv2.line(img, (set_point_x, set_point_y), (int(face['x']), int(face['y'])), (255, 0, 0), 2, cv2.FILLED)

    
    # calc speeds
    speed_x = int(pid_x(face['x']))
    speed_y = int(pid_y(face['y']))
    speed_z = -int(pid_z(face['z']))

    return img, (speed_x, speed_y, speed_z)


# start drone
if flying_enabled:
    drone.takeoff()

try:
    while True:

        pTime = time.time()
        img, speeds = findPose(drone.get_frame_read().frame)

        if speeds:         
            if flying_enabled:
                drone.send_rc_control(0, 0, 0, speeds[0])
                print(f"Speeds: {speeds}")
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