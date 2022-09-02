from threading import *
from _thread import *
from picamera import PiCamera
from picamera.array import PiRGBArray
from time import sleep
import numpy as np
import cv2
import socket
import select
import queue
import sys
from subprocess import check_output

class Server(Thread):
    IP = check_output(['hostname', '-I']).decode().rstrip()
    HOST = IP # The server's hostname or IP address
    PORT = 65437       # The port used by the server
    def init_settings(self):
        self.connected = False
        self.send_web_cam = False

    exit = False
    connected = False
    cap = cv2.VideoCapture(0)
    sleep(2)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    cap.set(cv2.CAP_PROP_FPS, 24)

    def __init__(self, queue):
        Thread.__init__(self)
        self.q = queue
        self.daemon = True
        self.start()

    def web_cam_str(self):
        ret, frame = self.cap.read()
        img_str = cv2.imencode(".jpg", frame)[1].tostring()
        return img_str
    
    def text_cmd(self, text):
        if text == "web_cam_off":
            self.send_web_cam = False
        elif text == "web_cam_on":
            self.send_web_cam = True
        elif text == "disconnect":
            self.connected = False
        elif text == "exit":
            self.connected = False
            self.exit = True
        else:
            self.q.put(text)

    def f_recv(self,c):
        while self.connected:
            r,_,_ = select.select([c], [], [], 0.1)
            if r:
                try:
                    data = c.recv(1024)
                    if not data:
                        self.connected = False
                        break
                    text = data.decode("utf-8")
                    self.text_cmd(text)
                except (ConnectionResetError, ConnectionAbortedError):
                    self.connected = False
    def write(self,text,c):
        c.send(text.encode())

    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((self.HOST, self.PORT))
        s.listen(0)
        while self.exit is False:
            conn, addr = s.accept()
            self.init_settings()
            with conn:
                print('Connected by', addr)
                self.connected = True
                self.write("Welcome",conn)
                start_new_thread(self.f_recv, (conn,))
                while self.connected:
                    if self.send_web_cam:
                        try:
                            conn.sendall(self.web_cam_str())
                            sleep(1/24)
                        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
                            self.connected = False
