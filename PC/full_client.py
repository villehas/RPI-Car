import socket
import numpy as np
import cv2
import threading
import select
import re
from time import sleep
class Client:
    def __init__(self, HOST, PORT):
        self.host = HOST
        self.port = PORT
        self.connected = False
        self.buffer = None
        self.image_buffer = b''
        self.img = None
        self.web_cam = False
        self.r_msg = None
        self.complete_image = None
    def write(self, message):
        self.buffer = message

    def Image(self):
        return self.img

    def recv_msg(self, data):
        self.r_msg = data.decode()

    def _connect(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((self.host, self.port))
                s.send(b"Hello world!")
                self.connected = True
            except ConnectionRefusedError:
                print("connected failed")
                self.connected = False
            while self.connected:
                r,_,_ = select.select([s], [], [], 0.1)
                if r:
                    try:
                        data = s.recv(8192)
                        # from received data search for start and end of JPEG file
                        # and combine data to a single JPEG image
                        f2 = re.search(b'\xFF\xD9', data) # end of JPEG file
                        f1 = re.search(b'\xFF\xD8', data) # start of JPEG file
                        if f2:
                            self.image_buffer += data[:f2.start()+2]
                            nparr = np.frombuffer(bytes(self.image_buffer), np.uint8)
                            decoded_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                            self.img = decoded_img
                        if f1:
                            self.image_buffer = data[f1.start():]
                        if not f1 and not f2:
                            self.image_buffer += data

                    except (ConnectionResetError, ConnectionAbortedError):
                        self.connected = False
                else:
                    self.web_cam = False

                if self.buffer is not None:
                    s.send(self.buffer.encode())
                    self.buffer = None

    def connect(self):
        t = threading.Thread(target=self._connect)
        t.daemon = True
        t.start()
