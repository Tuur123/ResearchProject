import cv2
import socket
import pickle
import face_recognition
from threading import Thread

HOST = ''
PORT = 5000
HEADERSIZE = 10

safe = 0
unsafe = 0
person_count = 0
checked_encodings = []

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)

conn, addr = s.accept()


def ShowUnsafeThread(img):
    cv2.imshow("UNSAFE PERSON", img)
    cv2.waitKey(0)

def ShowUnsafe(img):
    show_thread = Thread(args=(img,), target=ShowUnsafeThread)
    show_thread.start()

def Stoptracking():
    s.send(pickle.dumps(False))

def Keeptracking():
    s.send(pickle.dumps(True))


while True:
    full_msg = b''
    new_msg = True
    while True:
        msg = conn.recv(16)
        if new_msg:
            msglen = int(msg[:HEADERSIZE])
            new_msg = False
        full_msg += msg
        if len(full_msg)-HEADERSIZE == msglen:

            face_image, qr_data = pickle.loads(full_msg[HEADERSIZE:])
            unknown_encoding = face_recognition.face_encodings(face_image)[0]

            if qr_data == "CHECKED?":
                if checked_encodings == False:
                    print("Person not checked")
                
                else:
                    results = face_recognition.compare_faces(checked_encodings, unknown_encoding)

                    if results[0]:
                        print("This person is already checked")
                        # tell drone to stop tracking this person
                        Stoptracking()

                    else:
                        print("Person not checked")
                        # tell drone to keep tracking
                        Keeptracking()


            elif qr_data == "SAFE":
                print("This person is safe")

                # tell drone to stop tracking this person
                Stoptracking()

            elif qr_data == "UNSAFE":
                print("This person is not safe")
                ShowUnsafe(face_image)

                # tell drone to stop tracking this person
                Stoptracking()
                    
            else:
                print(f"Bad qr code: {qr_data}")

            new_msg = True
            full_msg = b""