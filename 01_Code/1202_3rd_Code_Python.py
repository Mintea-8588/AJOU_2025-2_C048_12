import cv2
import numpy as np
from PIL import Image
from keras import models
import os
import tensorflow as tf
import serial
import time

SERIAL_PORT = 'COM8'
model = models.load_model("tf_mnist_model2.h5")
video = cv2.VideoCapture(2)

py_serial = serial.Serial(port=SERIAL_PORT, baudrate=9600,)
time.sleep(0.1)

count = 5   # 딥러닝 횟수

# 숫자 입력 함수
def input_digits(direction_name):
    print(f"\n[{direction_name} 설정]")
    print(f"{direction_name}에 해당하는 숫자를 입력하세요.")
    print("모든 숫자를 입력한 후에는 00을 입력하세요.")

    digits = []
    while True:
        user_input = input("숫자 입력: ")

        try:
            if user_input == "00" :
                break

            num = int(user_input)

            if 0 <= num <= 9:
                if num not in digits:
                    digits.append(num)
                    print(f"  -> {num} 추가됨")
                else:
                    print("  -> 이미 있는 숫자입니다.")
            else:
                print("  -> 0~9 사이의 숫자를 입력하세요.")

        except ValueError:
            print("  -> 숫자가 아닙니다.")

    return digits

L_LIST = input_digits("좌회전")
print(f" 좌회전 숫자: {L_LIST}")

R_LIST = input_digits("우회전")
print(f" 우회전 숫자: {R_LIST}")

print("\n설정 완료! 아두이노 명령 대기 중...\n")

while True:
    # 데이터 입력 여부 확인
    if py_serial.readable():
        response = py_serial.readline()     # 데이터를 한 줄씩 읽기

        # 읽은 데이터가 비어있지 않으면 (0이 아니면)
        if response:
            line = response[:len(response)-1].decode()  # 디코딩

            if "SNAP" in line:
                for i in range(count):
                    video.read()
                _, frame = video.read()
                
                # 이미지 전처리
                im = Image.fromarray(frame, 'RGB')
                im2 = im.resize((28, 28))
                im2 = im2.convert('L')
                im2 = np.array(im2)
                im2 = im2/255.0
                im2 = im2.reshape((-1, 28, 28))

                # 예측
                prediction = model(im2).numpy()
                prob = tf.nn.softmax(prediction).numpy()
                predicted_digit = np.argmax(prob)

                # 판단 후 결과를 아두이노로 전송
                cmd = 'N'
                if predicted_digit in L_LIST:
                    cmd = 'L'
                elif predicted_digit in R_LIST:
                    cmd = 'R'

                py_serial.write(cmd.encode())
                print(f"SNAP -> 인식된 숫자:{predicted_digit} -> 명령:{cmd}")

            else:
                print(f"Arduino: {line}")

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video.release()
cv2.destroyAllWindows()
