import cv2
import numpy as np
from PIL import Image
import tensorflow as tf
import serial
import time
import os

# --- 설정 및 초기화 ---
SERIAL_PORT = 'COM8'

try:
    # 텐서플로우 모델 로드
    model = tf.keras.models.load_model("tf_mnist_model (2).h5")
except Exception as e:
    print(f"모델 로드 오류: {e}")
    os._exit(0)

# 비디오 캡처 초기화
video = cv2.VideoCapture(0)
if not video.isOpened():
    print("카메라를 열 수 없습니다.")
    os._exit(0)

# 시리얼 통신 초기화
try:
    py_serial = serial.Serial(port=SERIAL_PORT, baudrate=9600, timeout=0.1)
    time.sleep(1)
except serial.SerialException as e:
    print(f"시리얼 포트 연결 오류: {e}")
    os._exit(0)

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
    # 1. 카메라 프레임 읽기
    ret, frame = video.read()
    if not ret:
        print("프레임을 읽을 수 없습니다.")
        break
        
    # 2. 시리얼 통신 확인 및 'SNAP' 명령 처리
    if py_serial.readable():
        response = py_serial.readline()
        if response:
            try:
                line = response.decode().strip()
            except UnicodeDecodeError:
                line = ""

            if "SNAP" in line:
                
                # 'SNAP' 명령이 들어왔을 때만 예측 수행
                # 실제 스냅샷을 찍기 전에 버퍼를 비웁니다 (옵션)
                for _ in range(count):
                    video.read()
                
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
                # 'SNAP'이 아닌 메시지가 수신되었을 경우에도 predicted_digit과 cmd를 업데이트 해야
                # 화면에 표시할 수 있으나, 현재 코드는 'SNAP'시에만 예측하므로
                # 이 위치에서는 예측 결과가 없습니다.
                predicted_digit = "..." # 예측 중이 아님을 표시
                cmd = "N"


    # 3. 카메라 화면에 인식 결과 표시
    # 'SNAP'이 들어와 예측이 수행되었을 때 predicted_digit과 cmd가 업데이트됩니다.
    # 'SNAP'이 들어오지 않았을 경우 직전의 값이 유지되거나 초기값("...")이 사용될 것입니다.
    
    # 표시할 텍스트 준비
    if 'predicted_digit' in locals() and predicted_digit != "...":
        display_text = f"Digit: {predicted_digit}, Cmd: {cmd}"
    else:
        # 최초 실행 시 또는 SNAP 명령이 없었을 때의 기본 텍스트
        display_text = "Waiting for SNAP..." 

    # 텍스트를 프레임에 추가
    cv2.putText(
        img=frame, 
        text=display_text, 
        org=(10, 30), # 좌측 상단 위치
        fontFace=cv2.FONT_HERSHEY_SIMPLEX, 
        fontScale=1, 
        color=(0, 255, 0), # 녹색
        thickness=2
    )

    # 화면에 프레임 표시
    cv2.imshow('Camera Feed & Prediction', frame)
    # 
    
    # 4. 'q'를 누르면 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# --- 종료 처리 ---
video.release()
cv2.destroyAllWindows()
py_serial.close()
print("프로그램 종료.")
