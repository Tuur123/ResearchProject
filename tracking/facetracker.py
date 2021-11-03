from djitellopy import tello
import cv2

# drone = tello.Tello()
# drone.connect()

# print(f"Battery level: {drone.get_battery()}%")

cap = cv2.VideoCapture(0)

def findFace(img):

    detector = cv2.CascadeClassifier('models/haarcascade_frontalface_default.xml')
    grayScaled = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = detector.detectMultiScale(grayScaled, 1.2, 8)

    faceList = []
    areaList = []

    for (x, y, w, h) in faces:
        
 
        cx = x + w // 2
        cy = y + h // 2
        area = w * h

        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
        cv2.circle(img, (cx, cy), 5, (0, 255, 0), cv2.FILLED)

        faceList.append([cx, cy])
        areaList.append(area)

    if len(faceList) != 0:
        i = areaList.index(max(areaList))
        return img, [faceList[i], areaList[i]]
    else:
        return img, [[0, 0], 0]


try:
    while True:
        _, img = cap.read()
        img, info = findFace(img)
        print(info)
        cv2.imshow("Facedetector", img)
        cv2.waitKey(1)
except KeyboardInterrupt:
    cv2.destroyAllWindows()


