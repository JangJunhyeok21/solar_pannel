from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import functools
import cv2
import threading
import sys
import os
import RPi.GPIO as GPIO
import time

import spidev, time

GPIO.setmode(GPIO.BCM)



def analog_read(channel):
    r = spi.xfer2([1, (0x08+channel)<<4, 0])
    adc_out = ((r[1]&0x03)<<8) + r[2]
    return adc_out



spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz = 1000000

pin1= 6
pin3= 13
pin2= 19
pin4= 26
pin5= 4
pin7= 17
pin6= 27
pin8= 22

global speed , StepCnt, StepCnt2
speed = 0.003
StepCnt =0
StepCnt2 =0



GPIO.setup(pin1 , GPIO.OUT)
GPIO.setup(pin2 , GPIO.OUT)
GPIO.setup(pin3 , GPIO.OUT)
GPIO.setup(pin4 , GPIO.OUT)
GPIO.setup(pin5 , GPIO.OUT)
GPIO.setup(pin6 , GPIO.OUT)
GPIO.setup(pin7 , GPIO.OUT)
GPIO.setup(pin8 , GPIO.OUT)


def CW2(step):
    global speed, StepCnt2
    for i in range(step):
        GPIO.output(pin5,True)
        GPIO.output(pin6,False)
        GPIO.output(pin7,True)
        GPIO.output(pin8,False)
        time.sleep(speed)
        GPIO.output(pin5,False)
        GPIO.output(pin6,True)
        GPIO.output(pin7,True)
        GPIO.output(pin8,False)
        time.sleep(speed)
        GPIO.output(pin5,False)
        GPIO.output(pin6,True)
        GPIO.output(pin7,False)
        GPIO.output(pin8,True)
        time.sleep(speed)
        GPIO.output(pin5,True)
        GPIO.output(pin6,False)
        GPIO.output(pin7,False)
        GPIO.output(pin8,True)
        time.sleep(speed)
        StepCnt2 +=1

    GPIO.output(pin5,False)
    GPIO.output(pin6,False)
    GPIO.output(pin7,False)
    GPIO.output(pin8,False)



def CCW2(step):
    global speed, StepCnt2
    for i in range(step):
        GPIO.output(pin8,True)
        GPIO.output(pin7,False)
        GPIO.output(pin6,True)
        GPIO.output(pin5,False)
        time.sleep(speed)
        GPIO.output(pin8,False)
        GPIO.output(pin7,True)
        GPIO.output(pin6,True)
        GPIO.output(pin5,False)
        time.sleep(speed)
        GPIO.output(pin8,False)
        GPIO.output(pin7,True)
        GPIO.output(pin6,False)
        GPIO.output(pin5,True)
        time.sleep(speed)
        GPIO.output(pin8,True)
        GPIO.output(pin7,False)
        GPIO.output(pin6,False)
        GPIO.output(pin5,True)
        time.sleep(speed)
        StepCnt2 +=1
    GPIO.output(pin5,False)
    GPIO.output(pin6,False)
    GPIO.output(pin7,False)
    GPIO.output(pin8,False)

def CW(step):
    global speed , StepCnt
    for i in range(step):
        if StepCnt > 256:
            break
        GPIO.output(pin1,True)
        GPIO.output(pin2,False)
        GPIO.output(pin3,True)
        GPIO.output(pin4,False)
        time.sleep(speed)
        GPIO.output(pin1,False)
        GPIO.output(pin2,True)
        GPIO.output(pin3,True)
        GPIO.output(pin4,False)
        time.sleep(speed)
        GPIO.output(pin1,False)
        GPIO.output(pin2,True)
        GPIO.output(pin3,False)
        GPIO.output(pin4,True)
        time.sleep(speed)
        GPIO.output(pin1,True)
        GPIO.output(pin2,False)
        GPIO.output(pin3,False)
        GPIO.output(pin4,True)
        time.sleep(speed)
        StepCnt +=1

    GPIO.output(pin1,False)
    GPIO.output(pin2,False)
    GPIO.output(pin3,False)
    GPIO.output(pin4,False)



def CCW(step):
    global speed , StepCnt
    for i in range(step):
        if StepCnt < -256:
            break
        GPIO.output(pin4,True)
        GPIO.output(pin3,False)
        GPIO.output(pin2,True)
        GPIO.output(pin1,False)
        time.sleep(speed)
        GPIO.output(pin4,False)
        GPIO.output(pin3,True)
        GPIO.output(pin2,True)
        GPIO.output(pin1,False)
        time.sleep(speed)
        GPIO.output(pin4,False)
        GPIO.output(pin3,True)
        GPIO.output(pin2,False)
        GPIO.output(pin1,True)
        time.sleep(speed)
        GPIO.output(pin4,True)
        GPIO.output(pin3,False)
        GPIO.output(pin2,False)
        GPIO.output(pin1,True)
        time.sleep(speed)
        StepCnt -=1
    GPIO.output(pin1,False)
    GPIO.output(pin2,False)
    GPIO.output(pin3,False)
    GPIO.output(pin4,False)


video_capture = cv2.VideoCapture(-1)

fontLeftMenu= QFont('나눔고딕OTF', 15, QFont.Thin) #vnc화면에보이는

def sensorThread():
    global img , recogTime, idTxt
    direct = 0
    while True:
        adc0 = analog_read(0)
        adc1 = analog_read(1)
        adc2 = 0
        adc3 = analog_read(3)
        adc4 = analog_read(4)
        print(adc0, adc1, adc2, adc3, adc4)
        if(abs(adc0 - adc1) < 50):
            direct = 0
        if (adc0 > adc1):
            direct += 1
        elif (adc1 > adc0):
            direct -= 1

        if direct > 0:
            CCW(1)
            print('C', adc0-adc1 , adc1, adc0, direct)
            direct = 0
        elif direct < -0:
            CW(1)
            print('W', adc0-adc1 , adc1, adc0, direct)
            direct = 0
        else:
            print('S', adc0-adc1 , adc1, adc0)
        if adc4 < 100:
            if int(StepCnt2 / 128) % 2 == 0:
                CW2(1)
            else:
                CCW2(1)

        if adc3 > 859:
            batData = 100
        elif adc3 > 849:
            batData = 95
        elif adc3 > 840:
            batData = 90
        elif adc3 > 834:
            batData = 85
        elif adc3 > 822:
            batData = 80
        elif adc3 > 814:
            batData = 75
        elif adc3 > 808:
            batData = 70
        elif adc3 > 799:
            batData = 65
        elif adc3 > 791:
            batData = 60
        elif adc3 > 787:
            batData = 55
        elif adc3 > 785:
            batData = 50
        elif adc3 > 781:
            batData = 45
        elif adc3 > 777:
            batData = 40
        elif adc3 > 773:
            batData = 35
        elif adc3 > 771:
            batData = 30
        elif adc3 > 767:
            batData = 25
        elif adc3 > 763:
            batData = 20
        elif adc3 > 759:
            batData = 15
        elif adc3 > 754:
            batData = 10
        elif adc3 > 738:
            batData = 5
        else:
            batData = 0


        idTxt.setText('Battery : ' + str(batData)) # 화면에 갱신

    video_capture.release()
    cv2.destroyAllWindows()

def cam():
    global img , recogTime, idTxt
    openflag = 0
    while True:
        ret, frame = video_capture.read()
        cv2.imwrite('/home/pi/project/pic.jpg', frame)
        img.setPixmap(QPixmap('/home/pi/project/pic.jpg')) #카메라화면 표시

    video_capture.release()
    cv2.destroyAllWindows()

class hardCtl(QWidget): #메인화면 생성 클래스
    def __init__(self, parent=None):
        super(hardCtl, self).__init__(parent)
        global img , recogTime, idTxt

        img = QLabel(self) # 카메라 화면
        img.move(0,0)
        img.resize(640, 480)
        img.setPixmap(QPixmap('/home/pi/project/pic.jpg'))

        idTxt= QLabel(self)
        idTxt.setFont(fontLeftMenu)
        idTxt.resize(150,480)
        idTxt.move(650,0)

        t2 = threading.Thread(target = cam)
        t2.daemon = True
        t2.start()

        t1 = threading.Thread(target = sensorThread)
        t1.daemon = True
        t1.start()

        self.showFullScreen()

app = QApplication(sys.argv)
sb = hardCtl()
sb.resize(800, 480)
sb.move(0, 0)

sys.exit(app.exec_())
