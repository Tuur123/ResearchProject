import socket
import time

HOST = '192.168.8.49'
PORT = 5000

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    print("Connected")
    while True:
        print("Sending data")
        s.sendall(b'Hello, world')
        print("Recieving data")
        data = s.recv(1024)
        print('Echoing: ', repr(data))

        time.sleep(1)