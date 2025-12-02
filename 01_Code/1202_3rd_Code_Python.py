import cv2
import numpy as np
from PIL import Image
import tensorflow as tf
import serial
import time
import os # os 모듈을 사용하여 프로그램 종료

# --- 설정 및 초기화 ---
SERIAL_PORT = 'COM8'

try:
    model = tf.keras.models.load_model("tf_mnist_model.h5")
except Exception as e:
    print(f"모델 로드 오류: {e}")
    os._exit(0) # sys.exit() 대신 os._exit(0) 사용

video = cv2.VideoCapture(0)
if not video.isOpened():
    print("카메라를 열 수 없습니다.")
    os._exit(0) # sys.exit() 대신 os._exit(0) 사용

try:
    py_serial = serial.Serial(port=SERIAL_PORT, baudrate=9600, timeout=0.1)
    time.sleep(1)
except serial.SerialException as e:
    print(f"시리얼 포트 연결 오류: {e}")
    os._exit(0) # sys.exit() 대신 os._exit(0) 사용

count = 5

# --- 숫자 입력 함수 ---
def input_digits(direction_name):
    print(f"\n[{direction_name} 설정]")
    print(f"{direction_name}에 해당하는 숫자를 입력하세요.")
    print("모든 숫자를 입력한 후에는 00을 입력하세요.")
    digits = []
    while True:
        user_input = input("숫자 입력: ")
        try:
            if user_input == "00":
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

# --- 메인 루프 ---
while True:
    if py_serial.readable():
        response = py_serial.readline()
        if response:
            try:
                line = response.decode().strip()
            except UnicodeDecodeError:
                line = ""

            if "SNAP" in line:
                for _ in range(count):
                    video.read()
                
                _, frame = video.read()
                
                # 이미지 전처리 (픽셀 반전 없이 정규화)
                im = Image.fromarray(frame, 'RGB')
                im2 = im.resize((28, 28))
                im2 = im2.convert('L')
                
                im2_array = np.array(im2, dtype=np.float32)
                
                # 픽셀 반전 없이 정규화만 수행 (0.0 ~ 1.0)
                im2_processed = im2_array / 255.0
                
                # 배치 차원 추가: (1, 28, 28)
                final_input = im2_processed.reshape((1, 28, 28))

                # 예측
                prediction = model.predict(final_input, verbose=0) 
                
                # 가장 높은 확률의 인덱스 찾기
                predicted_digit = np.argmax(prediction, axis=1)[0]

                # 명령 판단 및 전송
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
py_serial.close()
print("프로그램 종료.")
