import queue
from server import Server
from motor import Motor
from time import sleep

if __name__ == '__main__':
    motor = Motor()
    print("Motor up!")
    q = queue.Queue(1)
    server = Server(q)
    print("Server up!")
    while True:
        try:
            text = q.get(block=True, timeout=1)
            print(text)
            motor.motor_cmd(text)
        except:
            pass

        if server.exit:
            print("Exiting")
            motor.exit()
            break
        sleep(0.1)
