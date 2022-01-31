import time
from threading import Thread

import cv2
import mediapipe as mp
from djitellopy import tello
from pyzbar.pyzbar import decode
from simple_pid import PID

flying_enabled = False
searching = True
track_time_out = False
track_timeout_time = 0


# init drone
drone = tello.Tello()
drone.connect()
drone.streamon()

# check battery
print(f"Battery level: {drone.get_battery()}%")

# constants
img_h, img_w = 720, 960
set_point_x = img_w // 2
set_point_y = img_h // 3
set_point_z = 100 # distance between eye points

# detector
poseDetector = mp.solutions.pose.Pose(min_detection_confidence=0.85, min_tracking_confidence=0.85)
 
# mp drawing
mpDraw = mp.solutions.drawing_utils

# PIDs
pid_x = PID(-0.15, -0.7, -0.1, setpoint=set_point_x, sample_time = 0.01)
pid_y = PID(-0.15, -0.7, -0.1, setpoint=set_point_y, sample_time = 0.01)

pid_x.output_limits = (-25, 25)
pid_y.output_limits = (-25, 25)

# CV functions
def findPose(img):

    results = poseDetector.process(img)
    landmarks = results.pose_landmarks

    if landmarks:
        return trackPose(img, landmarks.landmark)
    else:
        return img, None, True, False
   
def trackPose(img, landmark): 

    track_time_out = False
    searching = False

    # face keypoints
    face = {'x': landmark[0].x * img_w,
            'y': landmark[0].y * img_h,
            'z': (landmark[3].x - landmark[6].x) * img_w}


    # calc errors
    errors = (abs(face['x'] - set_point_x), abs(face['y'] - set_point_y), abs(face['z'] - set_point_z))

    # calc speeds
    speeds = [int(pid_x(face['x'])), -int(pid_y(face['y'])), 0]

    if face['z'] < 120:
        speeds[2] = 25
    if face['z'] > 140:
        speeds[2] = -25


    if face['z'] > 100 and face['z'] < 140: # if distance to face is good check for qr code

        codes = decode(img)

        if codes: # we can detect multiple codes
            for qr in codes:
                
                x, y, w, h = qr.rect # get qr location, has to be in proximity of hand landmark

                x = x-50
                y = y-50
                w = w+100
                h = h+100

                left = {'x': landmark[21].x * img_w,
                        'y': landmark[21].y * img_h}

                right = {'x': landmark[22].x * img_w,
                        'y': landmark[22].y * img_h}

                if (x < left['x'] < (x + w) and y < left['y'] < (y + h)) or (x < right['x'] < (x + w) and y < right['y'] < (y + h)): # make sure the person we are tracking is holding the qr
                    
                    # get face from frame
                    x = int(landmark[0].x * img_w) - 200
                    y = int(landmark[0].y * img_h) - 200

                    w = int(landmark[0].x * img_w) + 50
                    h = int(landmark[0].y * img_h) + 100
                    face_image = img[x:x+w,y:y+h]

                    cv2.putText(face_image, f"{qr.data.decode('utf-8')}", (75, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 1)

                    cv2.imshow("Face", face_image)
                    track_time_out = True

    # keep pid loop from oscillating
    for idx, error in enumerate(errors):
        if error < 100:
            speeds[idx] = 0

    # draw face keypoints
    img = cv2.circle(img, (set_point_x, set_point_y), 5, (255, 0, 0), cv2.FILLED) # setpoint
    img = cv2.circle(img, (int(face['x']), int(face['y'])), 5, (0, 0, 255), cv2.FILLED) # face location
    img = cv2.line(img, (set_point_x, set_point_y), (int(face['x']), int(face['y'])), (255, 0, 0), 2, cv2.FILLED)
    
    # draw error tolerance
    img = cv2.line(img, ((set_point_x - 50), set_point_y), ((set_point_x + 50), set_point_y), (0, 255, 0), 2, cv2.FILLED) # x
    img = cv2.line(img, (set_point_x, (set_point_y - 50)), (set_point_x, (set_point_y + 50)), (0, 255, 0), 2, cv2.FILLED) # y

    return img, speeds, searching, track_time_out


# start drone
if flying_enabled:

    def fly(drone):
        time.sleep(2) # wait until video stream start before takeoff
        drone.takeoff()

    Thread(target=fly, args=(drone,), name="Takeoff Thread").start()

try:
    while True:

        pTime = time.time()

        img = drone.get_frame_read().frame

        if not track_time_out:
            img, speeds, searching, track_time_out = findPose(img)
            
            if speeds:
                cv2.putText(img, f"TRACKING", (500, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 1)     
                if flying_enabled:
                    if drone.get_height() < 150: # if height gets too low we slowly let the drone climb
                        speeds[1] = 20
                    drone.send_rc_control(0, speeds[2], speeds[1], speeds[0])
                track_timeout_time = time.time()                

        if searching and flying_enabled:
            cv2.putText(img, f"SEARCHING", (500, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 1)
            if drone.get_height() < 150: # if height gets too low we slowly let the drone climb
                drone.send_rc_control(0, 0, 20, 10)
            else:
                drone.send_rc_control(0, 0, 0, 10)
            
        if track_time_out:
            if time.time() - track_timeout_time > 5:
                searching = False
                track_time_out = False

        try:
            fps = int(1 / (time.time() - pTime))
        except ZeroDivisionError:
            fps = "999+"

        cv2.putText(img, f"{fps} fps", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 1)
        cv2.putText(img, f"{drone.get_battery()}% Battery", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 1)
        cv2.imshow("Stream", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            if flying_enabled:
                drone.land()      
            cv2.destroyAllWindows()
            break

except KeyboardInterrupt:
    if flying_enabled:
        drone.land()
    cv2.destroyAllWindows()