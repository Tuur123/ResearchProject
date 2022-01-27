import cv2
from threading import Thread
import face_recognition


class CheckThread(Thread):
   def __init__(self, qr_image, face_image, qr_data, person_count):
       # Call the Thread class's init function
       Thread.__init__(self)
       self.qr_image = qr_image
       self.face_image = face_image
       self.qr_data = qr_data
       self.person_count = person_count


   # Override the run() function of Thread class
   def run(self):

        print(f"Person {self.person_count} is {self.qr_data}")

        if self.qr_data == "UNSAFE":
            cv2.imshow("UNSAFE PERSON", self.face_image)