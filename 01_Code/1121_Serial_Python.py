import serial
import time
py_serial = serial.Serial(port='COM8', baudrate=9600,)

while True:
    comment = input("아두이노에게 내릴 명령: ")
    py_serial.write(commend.encode())
    time.sleep(0.1)
    if py_serial.readable():
        response = py_serial.readline()
        print(response[:len(response)-1]/decode())
