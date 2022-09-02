import cv2
import sys
import socket
import threading
from time import sleep
from full_client import Client
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QPushButton, QSlider
from PyQt5.QtCore import QThread, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap

client = Client('192.168.10.61', 65437)

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.width=800
        self.height=600
        self.initUI()

    def button_connect_clicked(self):
        if client.connected:
            client.write("disconnect")
        else:
            client.connect()

    def button_camera_clicked(self):
        if client.connected:
            if client.web_cam:
                client.write("web_cam_off")
            else:
                client.write("web_cam_on")

    def button_exit_clicked(self):
        client.write("exit")
        sleep(0.5)
        sys.exit()

    def _updateImage(self):
        while True:
            image = client.Image()
            if image is not None:
                img_height, img_width, channel = image.shape
                bytesPerLine = 3 * img_width
                qImg = QImage(image.data, img_width, img_height, bytesPerLine, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(qImg)
                self.label.setPixmap(pixmap)
                self.label.move(self.width/2-img_width/2, 10)
            sleep(1/24)

        print("_updateImage")

    def keyPressEvent(self, e):
        if not e.isAutoRepeat():
            if e.key() == Qt.Key_Up:
                client.write("UP_on")
            elif e.key() == Qt.Key_Down:
                client.write("DOWN_on")
            elif e.key() == Qt.Key_Left:
                client.write("LEFT_on")
            elif e.key() == Qt.Key_Right:
                client.write("RIGHT_on")

    def keyReleaseEvent(self, e):
        if not e.isAutoRepeat():
            if e.key() == Qt.Key_Up:
                client.write("UP_off")
            elif e.key() == Qt.Key_Down:
                client.write("DOWN_off")
            elif e.key() == Qt.Key_Left:
                client.write("LEFT_off")
            elif e.key() == Qt.Key_Right:
                client.write("RIGHT_off")

    def _updateLabels(self):
        while True:
            if client.connected:
                self.button_connect.setText("Disconnect")
            else:
                self.button_connect.setText("Connect")
            if client.web_cam:
                self.button_camera.setText("Camera Off")
            else:
                self.button_camera.setText("Camera On")

            self.text_label.setText(client.r_msg)
            sleep(0.1)

    def sliderValue(self):
        size = self.slider.value()
        self.slider_text.setText("Speed {}".format(size))
        client.write("Speed {}".format(size))
    def updateLabels(self):
        t2 = threading.Thread(target=self._updateLabels)
        t2.daemon = True
        t2.start()

    def updateImage(self):
        t1 = threading.Thread(target=self._updateImage)
        t1.daemon = True
        t1.start()

    def initUI(self):
        self.setWindowTitle("Robot controller")
        self.setGeometry(1920/2-self.width/2,1200/2-self.height/2,self.width,self.height)
        # create a label
        self.label = QLabel(self)
        self.label.move(10, 10)
        self.label.resize(640, 360)
        self.text_label = QLabel(self)
        self.text_label.move(90, 460)
        self.text_label.resize(160,30)
        self.button_connect = QPushButton(self)
        self.button_connect.move(10, 400)
        self.button_connect.setText("Connect")
        self.button_connect.setFocusPolicy(Qt.NoFocus)
        self.button_connect.clicked.connect(self.button_connect_clicked)
        self.button_camera = QPushButton(self)
        self.button_camera.move(90, 400)
        self.button_camera.setText("Camera")
        self.button_camera.setFocusPolicy(Qt.NoFocus)
        self.button_camera.clicked.connect(self.button_camera_clicked)
        self.button_exit= QPushButton(self)
        self.button_exit.move(700, 550)
        self.button_exit.setText("Exit")
        self.button_exit.setFocusPolicy(Qt.NoFocus)
        self.button_exit.clicked.connect(self.button_exit_clicked)
        self.slider_text = QLabel(self)
        self.slider_text.move(610, 400)
        self.slider_text.resize(120,15)
        self.slider_text.setText("Speed")
        self.slider = QSlider(Qt.Horizontal, self)
        self.slider.move(600, 425)
        self.slider.setFocusPolicy(Qt.StrongFocus)
        self.slider.setTickPosition(QSlider.TicksBothSides)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setValue(50)
        self.slider.setTickInterval(10)
        self.slider.setSingleStep(1)
        self.slider.setFocusPolicy(Qt.NoFocus)
        self.slider.valueChanged.connect(self.sliderValue)
        self.updateImage()
        self.updateLabels()
        self.show()

if __name__ == '__main__':
    sleep(1)
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
