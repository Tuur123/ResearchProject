import socket
import pickle

import cv2
import face_recognition

HOST = ''
PORT = 5000
HEADERSIZE = 10

safe = 0
unsafe = 0

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)

conn, addr = s.accept()

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
            face_image, qr_image, qr_data = pickle.loads(full_msg[HEADERSIZE:])

            



            new_msg = True
            full_msg = b""