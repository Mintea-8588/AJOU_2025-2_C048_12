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

count = 5 # 이 값은 버퍼 비우기에만 사용

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

# --- 제한 숫자 리스트 ---
ALLOWED_DIGITS = [1, 3, 5, 7, 8, 9] 
SAMPLE_COUNT = 10 # 10회 샘플링
SCORE_WEIGHTS = [3, 2, 1] # 1순위 3점, 2순위 2점, 3순위 1점

# --- 이미지 전처리 함수 ---
def preprocess_frame(frame):
    """카메라 프레임을 모델 입력 형식에 맞게 전처리합니다."""
    # OpenCV BGR -> PIL RGB 변환 (Image.fromarray가 기본적으로 수행)
    im = Image.fromarray(frame, 'RGB')
    
    # 28x28로 리사이즈 및 흑백 변환 (L: Luminosity)
    im2 = im.resize((28, 28))
    im2 = im2.convert('L')
    
    im2_array = np.array(im2, dtype=np.float32)
    
    # 픽셀 반전 없이 정규화만 수행 (0.0 ~ 1.0)
    im2_processed = im2_array / 255.0
    
    # 배치 차원 추가: (1, 28, 28)
    final_input = im2_processed.reshape((1, 28, 28))
    
    return final_input

# --- 메인 루프 ---
predicted_digit = "..." # 예측 중이 아님을 표시
cmd = "N"

while True:
    # 1. 카메라 프레임 읽기
    ret, frame = video.read()
    if not ret:
        print("프레임을 읽을 수 없습니다.")
        break
        
    # 시리얼 통신 확인 및 'SNAP' 명령 처리
    if py_serial.readable():
        response = py_serial.readline()
        if response:
            try:
                line = response.decode().strip()
            except UnicodeDecodeError:
                line = ""

            if "SNAP" in line:
                print("\nSNAP 수신! 10회 샘플링 시작...")
                
                # 'SNAP' 명령이 들어왔을 때만 예측 수행
                # 실제 스냅샷을 찍기 전에 버퍼를 비웁니다 (옵션)
                for _ in range(count):
                    video.read()
                    
                # 투표를 위한 점수 딕셔너리 초기화 (0-9)
                scores = {i: 0 for i in range(10)}
                
                # 10회 샘플링 및 예측
                for i in range(SAMPLE_COUNT):
                    # 새로운 프레임 읽기
                    ret_sample, frame_sample = video.read()
                    if not ret_sample:
                        print(f"프레임 읽기 실패: 샘플링 {i+1}/{SAMPLE_COUNT}")
                        continue
                        
                    # 전처리
                    input_data = preprocess_frame(frame_sample)
                    
                    # 예측
                    prediction = model.predict(input_data, verbose=0)[0] # (10,) 배열
                    
                    # 확률이 높은 순서대로 정렬된 인덱스 (숫자)
                    # 내림차순 정렬: [9, 7, 5, ...]
                    ranked_digits = np.argsort(prediction)[::-1]
                    
                    # 상위 3개 예측에 가중치 부여
                    for rank in range(min(3, len(ranked_digits))):
                        digit = ranked_digits[rank]
                        weight = SCORE_WEIGHTS[rank]
                        scores[digit] += weight
                        
                print(f"샘플링 완료. 총 점수: {scores}")

                # =========================================================
                # 3. 투표 결과에서 최종 명령을 결정 (L 그룹 vs R 그룹 최고 점수 비교)
                
                # L, R 리스트와 ALLOWED_DIGITS의 교집합을 구하여 실제 명령 판단에 사용할 숫자만 남깁니다.
                L_DIGITS_FOR_DECISION = [d for d in L_LIST if d in ALLOWED_DIGITS]
                R_DIGITS_FOR_DECISION = [d for d in R_LIST if d in ALLOWED_DIGITS]

                # L 그룹에서 가장 높은 점수와 해당 숫자 찾기
                best_l_score = -1
                best_l_digit = "..."
                for digit in L_DIGITS_FOR_DECISION:
                    if scores.get(digit, 0) > best_l_score:
                        best_l_score = scores[digit]
                        best_l_digit = digit

                # R 그룹에서 가장 높은 점수와 해당 숫자 찾기
                best_r_score = -1
                best_r_digit = "..."
                for digit in R_DIGITS_FOR_DECISION:
                    if scores.get(digit, 0) > best_r_score:
                        best_r_score = scores[digit]
                        best_r_digit = digit

                # 4. L/R 그룹 점수 비교 및 명령 판단
                cmd = 'N'
                final_predicted_digit = "None"
                final_max_score = 0

                if best_l_score > best_r_score and best_l_score > 0:
                    cmd = 'L'
                    final_predicted_digit = best_l_digit
                    final_max_score = best_l_score
                elif best_r_score > best_l_score and best_r_score > 0:
                    cmd = 'R'
                    final_predicted_digit = best_r_digit
                    final_max_score = best_r_score
                else: # 점수가 같거나 (둘 다 0일 포함), 두 그룹 모두 0점인 경우
                    cmd = 'N'
                    if best_l_score == best_r_score and best_l_score > 0:
                        # 동점일 경우, 화면 표시용으로 ALLOWED_DIGITS 중 최고 점수 숫자를 찾습니다.
                        temp_scores = {d: scores[d] for d in ALLOWED_DIGITS}
                        final_predicted_digit = max(temp_scores, key=temp_scores.get)
                        final_max_score = temp_scores[final_predicted_digit]
                        print(f"경고: L/R 그룹 동점 (점수:{final_max_score}). 명령 N 전송.")
                    else:
                        # L/R 그룹 모두 0점
                        print("경고: L/R 그룹 모두 0점입니다. 명령 N 전송.")

                # 명령 전송
                py_serial.write(cmd.encode())
                predicted_digit = final_predicted_digit # 화면 표시에 사용
                max_score = final_max_score            # 화면 표시에 사용
                print(f"최종 인식 숫자:{predicted_digit} (점수:{max_score}) -> 명령:{cmd}")
                # =========================================================
                
            else:
                # 'SNAP'이 아닌 메시지 처리
                print(f"Arduino: {line}")
                predicted_digit = "..." # 예측 중이 아님을 표시
                cmd = "N"


    # 3. 카메라 화면에 인식 결과 표시
    
    # 표시할 텍스트 준비
    if predicted_digit != "...":
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
    
    # 4. 'q'를 누르면 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# --- 종료 처리 ---
video.release()
cv2.destroyAllWindows()
py_serial.close()
print("프로그램 종료.")
