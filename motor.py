import RPi.GPIO as GPIO
import re

class Motor:
    def __init__(self):
        # setup motor controller pself.ins
        # a = left side
        # b = right side
        self.ina1 = 24
        self.ina2 = 23
        self.ena = 25
        self.inb1 = 17
        self.inb2 = 27
        self.enb = 22
        self.speed = 50 # Startself.ing speed value, must be between 0-100. Too low startself.ing value wont run the motors.
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.ina1,GPIO.OUT)
        GPIO.setup(self.ina2,GPIO.OUT)
        GPIO.setup(self.ena,GPIO.OUT)
        GPIO.output(self.ina1,GPIO.LOW)
        GPIO.output(self.ina2,GPIO.LOW)
        GPIO.setup(self.inb1,GPIO.OUT)
        GPIO.setup(self.inb2,GPIO.OUT)
        GPIO.setup(self.enb,GPIO.OUT)
        GPIO.output(self.inb1,GPIO.LOW)
        GPIO.output(self.inb2,GPIO.LOW)
        self.pa=GPIO.PWM(self.ena,2000)
        self.pb=GPIO.PWM(self.enb,2000)
        self.pa.start(self.speed)
        self.pb.start(self.speed)

        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

    def stop(self):
        GPIO.output(self.ina1,GPIO.LOW)
        GPIO.output(self.ina2,GPIO.LOW)
        GPIO.output(self.inb1,GPIO.LOW)
        GPIO.output(self.inb2,GPIO.LOW)
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

    def motor_run(self):
        if self.up_pressed:
            GPIO.output(self.ina1,GPIO.LOW)
            GPIO.output(self.ina2,GPIO.HIGH)
            GPIO.output(self.inb1,GPIO.LOW)
            GPIO.output(self.inb2,GPIO.HIGH)
            self.pa.ChangeDutyCycle(self.speed)
            self.pb.ChangeDutyCycle(self.speed)
        elif self.down_pressed:
            GPIO.output(self.ina1,GPIO.HIGH)
            GPIO.output(self.ina2,GPIO.LOW)
            GPIO.output(self.inb1,GPIO.HIGH)
            GPIO.output(self.inb2,GPIO.LOW)
            self.pa.ChangeDutyCycle(self.speed)
            self.pb.ChangeDutyCycle(self.speed)
        elif self.right_pressed:
            GPIO.output(self.ina1,GPIO.LOW)
            GPIO.output(self.ina2,GPIO.HIGH)
            GPIO.output(self.inb1,GPIO.HIGH)
            GPIO.output(self.inb2,GPIO.LOW)
            self.pa.ChangeDutyCycle(self.speed)
            self.pb.ChangeDutyCycle(self.speed)
        elif self.left_pressed:
            GPIO.output(self.ina1,GPIO.HIGH)
            GPIO.output(self.ina2,GPIO.LOW)
            GPIO.output(self.inb1,GPIO.LOW)
            GPIO.output(self.inb2,GPIO.HIGH)
            self.pa.ChangeDutyCycle(self.speed)
            self.pb.ChangeDutyCycle(self.speed)
        else:
            self.stop()

    def motor_cmd(self,cmd):
        if cmd == "UP_on" and not(self.down_pressed or self.left_pressed or self.right_pressed):
            self.up_pressed = True
        elif cmd == "UP_off":
            self.up_pressed = False
        elif cmd == "DOWN_on" and not(self.up_pressed or self.left_pressed or self.right_pressed):
            self.down_pressed = True
        elif cmd == "DOWN_off":
            self.down_pressed = False
        elif cmd == "LEFT_on" and not(self.down_pressed or self.up_pressed or self.right_pressed):
            self.left_pressed = True
        elif cmd == "LEFT_off":
            self.left_pressed = False
        elif cmd == "RIGHT_on" and not(self.down_pressed or self.left_pressed or self.up_pressed):
            self.right_pressed = True
        elif cmd == "RIGHT_off":
            self.right_pressed = False
        elif cmd[:5] == "Speed":
            re_speed = int(re.search(r'\d+', cmd).group())
            # using 8x1.2V(9.6V total) batteries to power 3-6V DC motor
            # L298D motor controller has ~2v voltage drop
            # So max speed is set to 75% duty cycle to supply less than 6V
            if re_speed >= 0 and re_speed <= 75:
                print(re_speed)
                self.speed = re_speed
            elif re_speed > 75:
                print(75)
                self_speed = re_speed
        self.motor_run()

    def exit(self):
        GPIO.cleanup()
