from djitellopy import tello
from simple_pid import PID
import time
import cv2


drone = tello.Tello()
drone.connect()
drone.streamon()

# drone.takeoff()

print(f"Battery level: {drone.get_battery()}%")


img_w, img_h = 480, 360


set_point_x = img_w // 2
set_point_y = img_h // 2
set_point_z = (img_w * img_h) // 4

pid_x = PID(1, 0.1, 0.1, setpoint=set_point_x, sample_time = None)
pid_y = PID(1, 0.1, 0.1, setpoint=set_point_y, sample_time = None)
pid_z = PID(1, 0.1, 0.1, setpoint=set_point_z, sample_time = None)

pid_x.output_limits = (-100, 100)
pid_y.output_limits = (-100, 100)
pid_z.output_limits = (-100, 100)


def findFace(img):

    detector = cv2.CascadeClassifier('models/haarcascade_frontalface_default.xml')
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
        return img, {'x': faceList[i][0], 'y': faceList[i][1], 'z': areaList[i]}
    else:
        return img, None

def trackFace(face):

    error_x = face['x']
    error_y = face['y']

    speed_x = int(pid_x(error_x))
    speed_y = int(pid_y(error_y))
    speed_z = int(pid_z(face['z']))

    print(f"Errors: {error_x - set_point_x}, {error_y - set_point_y}, {face['z'] - set_point_z}. Speeds: {speed_x}, {speed_y}, {speed_z}")

    return speed_x, speed_y, speed_z

try:
    while True:

        pTime = time.time()

        img = drone.get_frame_read().frame
        img = cv2.resize(img, (img_w, img_h))
        img, face = findFace(img)

        if face != None:
            x, y, z = trackFace(face)
            # drone.send_rc_control(0, z, y, x)
        else:
            # drone.send_rc_control(0, 0, 0, 0)
            pass
            

        fps = int(1 / (time.time() - pTime))
        cv2.putText(img, f"{fps} fps", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        cv2.imshow("Stream", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            drone.land()
            cv2.destroyAllWindows()
            break

except KeyboardInterrupt:
    drone.land()
    cv2.destroyAllWindows()