import cv2
import numpy as np
from PIL import Image
import tensorflow as tf
import os 
import time # sleep 함수를 추가하여 출력 속도를 제어할 수 있습니다.

# --- 설정 및 초기화 ---
MODEL_FILE = "tf_mnist_model (2).h5" 

try:
    model = tf.keras.models.load_model(MODEL_FILE)
    print(f"모델 '{MODEL_FILE}' 로드 성공.")
except Exception as e:
    print(f"모델 로드 오류: {e}")
    os._exit(0) 

video = cv2.VideoCapture(0)
if not video.isOpened():
    print("카메라를 열 수 없습니다.")
    os._exit(0) 

CAPTURE_SKIP_FRAMES = 5
SAMPLE_SIZE = 3 
REQUIRED_COUNT = 3 

# --- 숫자 입력 및 명령 리스트 설정 (이 부분은 이전과 동일) ---
def input_digits(direction_name):
    """사용자로부터 0~9 사이의 숫자를 입력받아 리스트로 반환합니다."""
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
print("\n설정 완료! 카메라 영상 인식 시작...\n")

# --- 메인 루프 변수 ---
command_history = [] 
last_confirmed_cmd = 'N' 
sample_counter = 0 # 현재 샘플링 횟수를 추적하는 카운터

# --- 메인 루프 ---
print("=" * 40)
print(" 실시간 숫자 인식 시작 (종료: 'q' 키 누름) ")
print("=" * 40)
while True:
    # 캡처 안정화를 위해 프레임 스킵
    for _ in range(CAPTURE_SKIP_FRAMES):
        video.read()
    
    ret, frame = video.read()
    if not ret:
        print("\n프레임을 읽을 수 없습니다. (비디오 스트림 종료)")
        break

    # --- 이미지 전처리 및 예측 ---
    im = Image.fromarray(frame, 'RGB')
    im2 = im.resize((28, 28))
    im2 = im2.convert('L')
    im2_array = np.array(im2, dtype=np.float32)
    im2_processed = im2_array / 255.0
    final_input = im2_processed.reshape((1, 28, 28))

    prediction = model.predict(final_input, verbose=0) 
    predicted_digit = np.argmax(prediction, axis=1)[0]

    # --- 명령 판단 (L, R, N 중 하나) ---
    current_cmd = 'N'
    if predicted_digit in L_LIST:
        current_cmd = 'L'
    elif predicted_digit in R_LIST:
        current_cmd = 'R'
    
    # --- 단독 출현 명령 확인 로직 (L/R만 3회 출현) ---
    command_history.append(current_cmd)
    
    # history 리스트의 크기를 3으로 유지 (FIFO)
    if len(command_history) > SAMPLE_SIZE:
        command_history.pop(0)

    # ----------------------------------------------------
    # 가독성 개선: 매 루프마다 출력하지 않고, 샘플링 상태만 표시
    # ----------------------------------------------------
    sample_counter += 1
    
    if len(command_history) == SAMPLE_SIZE:
        
        l_count = command_history.count('L')
        r_count = command_history.count('R')
        final_cmd = None
        
        # 1. 확정 명령 확인 (L만 3회 또는 R만 3회)
        if l_count == REQUIRED_COUNT and r_count == 0:
            final_cmd = 'L'
        elif r_count == REQUIRED_COUNT and l_count == 0:
            final_cmd = 'R'
        
        if final_cmd:
            # 확정된 명령을 콘솔에 강조하여 출력
            print("=" * 40)
            print(f"🚨 [명령 확정!] -> 최종 명령: {final_cmd} (Sample: {sample_counter})")
            print("=" * 40)
            last_confirmed_cmd = final_cmd
            
            # 확정 후 history 및 카운터 초기화
            command_history = []
            sample_counter = 0

        else:
            # L/R 단독 3회가 아닌 경우 (명령 불분명 또는 N만 존재)
            # 불필요한 콘솔 출력 대신, 'N' 명령으로 간주하고 리셋
            
            # N이 3번이거나 L/R이 섞여있어 확정되지 못한 경우
            # 이 시점에서 다음 샘플링을 위해 리셋하고 다음 3회 샘플링 시작
            if l_count == 0 and r_count == 0:
                 last_confirmed_cmd = 'N'
            
            # (디버깅용) 불필요한 출력 제거, 내부적으로 리셋만 수행
            command_history = []
            sample_counter = 0
            
    # --- 화면에 결과 표시 ---
    # 인식된 숫자와 현재 버퍼 상태를 화면에 표시하여 디버깅 및 가독성을 높입니다.
    current_hist_str = "/".join(command_history).ljust(SAMPLE_SIZE * 2, '_')
    status_text = f"Buffer: [{current_hist_str}]"
    
    result_text = f"인식: {predicted_digit} | 최종 명령: {last_confirmed_cmd}"
    
    color = (0, 255, 0) if last_confirmed_cmd in ('L', 'R') else (255, 255, 0)
    
    # 화면 상단에 버퍼 상태 출력
    cv2.putText(frame, status_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
    # 화면 하단에 최종 명령 출력
    cv2.putText(frame, result_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv2.LINE_AA)
    
    cv2.imshow('Digit Recognition (Clean Console Output)', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
        
    # 루프 속도를 약간 늦춰 콘솔 출력이나 화면 업데이트의 부담을 줄일 수 있습니다 (선택 사항).
    # time.sleep(0.01) 

# --- 종료 처리 ---
video.release()
cv2.destroyAllWindows()
print("\n프로그램 종료.")
