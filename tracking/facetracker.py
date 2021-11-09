from djitellopy import tello
from simple_pid import PID
from threading import Thread
from queue import Queue
import time
import cv2

# queue's
imgQueue = Queue()
faceQueue = Queue()
trackQueue = Queue()

imgQueue.maxsize = 1000

# init drone
drone = tello.Tello()
drone.connect()
drone.streamon()

# check battery
print(f"Battery level: {drone.get_battery()}%")

# constants
img_w, img_h = 480, 360
set_point_x = img_w // 2
set_point_y = img_h // 2
set_point_z = (img_w * img_h) // 12

# detector
detector = cv2.CascadeClassifier('models/haarcascade_frontalface_default.xml')

# PIDs
pid_x = PID(-1, -0.1, -0.1, setpoint=set_point_x, sample_time = None)
pid_y = PID(-1, -0.1, -0.1, setpoint=set_point_y, sample_time = None)
pid_z = PID(-1, -0.1, -0.1, setpoint=set_point_z, sample_time = None)

pid_x.output_limits = (-40, 40)
pid_y.output_limits = (-40, 40)
pid_z.output_limits = (-40, 40)

### THREADS ###
running = True

def getImg(imgQueue, drone):
    while running:
        imgQueue.put(drone.get_frame_read().frame)
        print("adding frame to q")

def findFace(imgQueue, faceQueue):

    while running:
        img = imgQueue.get()
        img = cv2.resize(img, (img_w, img_h))
        grayScaled = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = detector.detectMultiScale(grayScaled, 1.2, 5)

        faceList = []
        areaList = []

        for (x, y, w, h) in faces:
            
            cx = x + w // 2
            cy = y + h // 2
            area = w * h

            # face
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv2.circle(img, (cx, cy), 5, (0, 255, 0), cv2.FILLED)

            # drone target
            cv2.circle(img, (img_w//2, img_h//2), 10, (255, 0, 0), cv2.FILLED)
            cv2.line(img, (cx, cy), (img_w//2, img_h//2), (255, 0, 0), 2)

            faceList.append([cx, cy])
            areaList.append(area)

        if len(faceList) != 0:
            i = areaList.index(max(areaList)) # pick face closest to drone for tracking
            faceQueue.put(img, {'x': faceList[i][0], 'y': faceList[i][1], 'z': areaList[i]})

        else:
            faceQueue.put(img, None)

def trackFace(faceQueue, trackQueue):

    while running:

        img, errors = faceQueue.get()

        if errors != None:
            error_x = errors['x']
            error_y = errors['y']

            speed_x = int(pid_x(error_x))
            speed_y = int(pid_y(error_y))
            speed_z = -int(pid_z(errors['z']))

            print(f"Errors: {error_x - set_point_x}, {error_y - set_point_y}, {errors['z'] - set_point_z}. Speeds: {speed_x}, {speed_y}, {speed_z}")
            trackQueue.put(img, (speed_x, speed_y, speed_z))
        else:
            trackQueue.put(img, None)

imgThread = Thread(target=getImg(imgQueue, drone), daemon=True)
faceThread = Thread(target=findFace(imgQueue, faceQueue), daemon=True)
trackThread = Thread(target=trackFace(faceQueue, trackQueue), daemon=True)

imgThread.start()
faceThread.start()
trackThread.start()
### THREADS ###

# start drone
# drone.takeoff()

try:
    while True:

        pTime = time.time()
        img, speeds = trackQueue.get()

        if speeds != None:
            # drone.send_rc_control(0, speeds[0], speeds[1], speeds[2])
            print(speeds)
        else:
            # drone.send_rc_control(0, 0, 0, 0)
            pass

        fps = int(1 / (time.time() - pTime))
        cv2.putText(img, f"{fps} fps", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        cv2.imshow("Stream", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            # drone.land()
            running = False
            cv2.destroyAllWindows()
            break

except KeyboardInterrupt:
    # drone.land()
    running = False
    cv2.destroyAllWindows()