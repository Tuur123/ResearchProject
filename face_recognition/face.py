from email import message
import face_recognition
import socket
import pickle

HOST = ''
PORT = 5000
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)

conn, addr = s.accept()

while True:

    messagestr = ""

    while bytes("\n") not in messagestr:
        messagestr += conn.recv(1)

    messagestr = messagestr[:-2]

    data = pickle.loads(messagestr)

    print(data)