import math
import time
from threading import Thread

import cv2
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
from djitellopy import tello
from simple_pid import PID

gpus = tf.config.experimental.list_physical_devices('GPU')
for gpu in gpus:
    tf.config.experimental.set_memory_growth(gpu, True)

model = hub.load("models\movenet_multipose_lightning_1")
movenet = model.signatures['serving_default']

flying_enabled = False

# init frame saver
# saver = FrameSaver("eval/frames/frames.pkl")

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
set_point_z = 50 # distance between eye points should in pixels


# PIDs
pid_x = PID(-0.15, -0.7, -0.1, setpoint=set_point_x, sample_time = 0.01)
pid_y = PID(-0.2, -0.2, 0, setpoint=set_point_y, sample_time = 0.01)
pid_z = PID(1, 0.1, 0.1, setpoint=set_point_z, sample_time = 0.01)

pid_x.output_limits = (-100, 100)
pid_y.output_limits = (-100, 100)
pid_z.output_limits = (-100, 100)


# CV functions
def findPerson(img):

    # Resize image
    frame = img.copy()
    frame = tf.image.resize_with_pad(tf.expand_dims(frame, axis=0), 384,640)
    input_frame = tf.cast(frame, dtype=tf.int32)
    
    # Detection
    results = movenet(input_frame)

    '''
    We've used NumPy [:,:,:51] to grab all batch dimensions, all of the maximum number of people, and only the 51
    keypoint locations and scores because that's all we need to render our image. reshape((6,17,3) tells us that we're
    reshaping the keypoint to have 6 people, each person with 17 joints, each person having 3 values; the x, y, and confidence score.
    '''
    keypoints = results['output_0'].numpy()[:,:,:51].reshape((6,17,3))
    [print(score) for person in keypoints for score in person[:,2]]


    faces = [person[:3] for person in keypoints if any(score > 0.1 for score in person[:,2])]
    

    if not faces:
        return img, None, None
    else:
        return trackPerson(img, faces[0])
  


def trackPerson(img, facepoints): 

    # face average
    x = np.average(facepoints[:,0])
    y = np.average(facepoints[:,1])
    z = facepoints[:,0][1] - facepoints[:,0][2]
    
    face = {'x': x * img_w,
            'y': y * img_h,
            'z': z}

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

    return img, speeds, errors


# start drone
if flying_enabled:

    def fly(drone):
        drone.takeoff()
    Thread(target=fly, args=(drone,), name="Takeoff Thread").start()

try:
    while True:

        pTime = time.time()
        img, speeds, errors = findPerson(drone.get_frame_read().frame)

        if speeds:     

            if flying_enabled:
                drone.send_rc_control(0, 0, 0, speeds[0])
           
            # saver.saveFrame(img, speeds, errors)
            # print(f"Speeds: {speeds}")

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