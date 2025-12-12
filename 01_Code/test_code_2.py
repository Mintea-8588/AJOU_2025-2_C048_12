import cv2
import numpy as np
from PIL import Image
import tensorflow as tf
import os # os 모듈을 사용하여 프로그램 즉시 종료

# --- 설정 및 초기화 ---
# 모델 파일명을 요청에 따라 변경합니다.
MODEL_FILE = "tf_mnist_model (2).h5" 

try:
    # 텐서플로우 모델 로드
    model = tf.keras.models.load_model(MODEL_FILE)
    print(f"모델 '{MODEL_FILE}' 로드 성공.")
except Exception as e:
    print(f"모델 로드 오류: {e}")
    os._exit(0) # 모델 로드 실패 시 즉시 프로그램 종료

# 웹캠 비디오 캡처 초기화
video = cv2.VideoCapture(0)
if not video.isOpened():
    print("카메라를 열 수 없습니다.")
    os._exit(0) # 카메라 초기화 실패 시 즉시 프로그램 종료

# 안정적인 캡처를 위한 프레임 스킵 횟수 (선택적)
CAPTURE_SKIP_FRAMES = 5
SAMPLE_SIZE = 3 # ★ 샘플링 크기: 3회
REQUIRED_COUNT = 2 # ★ 확정을 위한 최소 횟수: 2회 (3회 중 2회 이상)

# --- 숫자 입력 및 명령 리스트 설정 ---
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

# 좌회전/우회전 숫자 설정
L_LIST = input_digits("좌회전")
print(f" 좌회전 숫자: {L_LIST}")
R_LIST = input_digits("우회전")
print(f" 우회전 숫자: {R_LIST}")
print("\n설정 완료! 카메라 영상 인식 시작...\n")

# --- 메인 루프 변수 ---
command_history = [] # 최근 명령을 저장할 리스트 (최대 3개)
last_confirmed_cmd = 'N' # 마지막으로 확정된 명령 (화면 표시에 사용)

# --- 메인 루프 ---
print("--- 실시간 숫자 인식 시작 (종료: 'q' 키 누름) ---")
while True:
    # 캡처 안정화를 위해 프레임 스킵
    for _ in range(CAPTURE_SKIP_FRAMES):
        video.read()
    
    # 실제 인식에 사용할 프레임 읽기
    ret, frame = video.read()
    
    if not ret:
        print("프레임을 읽을 수 없습니다. (비디오 스트림 종료)")
        break

    # --- 이미지 전처리 및 예측 ---
    im = Image.fromarray(frame, 'RGB')
    im2 = im.resize((28, 28))
    im2 = im2.convert('L')
    
    im2_array = np.array(im2, dtype=np.float32)
    im2_processed = im2_array / 255.0 # 정규화 (0.0 ~ 1.0)
    final_input = im2_processed.reshape((1, 28, 28)) # 배치 차원 추가

    prediction = model.predict(final_input, verbose=0) 
    predicted_digit = np.argmax(prediction, axis=1)[0]

    # --- 명령 판단 (L, R, N 중 하나) ---
    current_cmd = 'N'
    if predicted_digit in L_LIST:
        current_cmd = 'L'
    elif predicted_digit in R_LIST:
        current_cmd = 'R'
    
    # --- 다수결 명령 확인 로직 (샘플링 3회 중 2회 이상) ---
    command_history.append(current_cmd)
    
    # history 리스트의 크기를 3으로 유지 (FIFO)
    if len(command_history) > SAMPLE_SIZE:
        command_history.pop(0)

    # 인식된 숫자는 매번 출력
    print(f"인식된 숫자:{predicted_digit} -> 임시 명령:{current_cmd}", end='')
    
    if len(command_history) == SAMPLE_SIZE:
        # L과 R의 출현 횟수 계산
        l_count = command_history.count('L')
        r_count = command_history.count('R')
        
        final_cmd = None
        
        if l_count >= REQUIRED_COUNT:
            # L이 2회 이상 나왔을 때 확정
            final_cmd = 'L'
        elif r_count >= REQUIRED_COUNT:
            # R이 2회 이상 나왔을 때 확정
            final_cmd = 'R'
        elif l_count == 0 and r_count == 0:
            # L과 R이 전혀 없으면 N이 3회 (혹은 N이 3회)
            final_cmd = 'N'
        
        if final_cmd:
            # 확정된 명령을 출력
            print(f" [★ 확정 명령: {final_cmd}]", end='')
            last_confirmed_cmd = final_cmd
            
            # 확정 후 다시 샘플링을 시작하기 위해 history 초기화
            command_history = []
        elif l_count == 1 and r_count == 1:
            # L 1개, R 1개, N 1개인 경우 등 (명령이 불분명할 경우 N으로 처리하고 초기화)
            print(" [★ 확정 명령: N (다수결 불분명)]", end='')
            last_confirmed_cmd = 'N'
            command_history = []


    print() # 줄바꿈

    # --- 화면에 결과 표시 ---
    result_text = f"인식: {predicted_digit} | 최종 명령: {last_confirmed_cmd}"
    # 확정 명령이 출력되었을 때는 색상을 변경
    color = (0, 255, 0) if last_confirmed_cmd in ('L', 'R') else (255, 255, 0)
    
    cv2.putText(frame, result_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv2.LINE_AA)
    
    # 결과가 적용된 이미지 화면 출력
    cv2.imshow('Digit Recognition (Majority Filter)', frame)

    # 'q' 키를 누르면 루프 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# --- 종료 처리 ---
video.release()
cv2.destroyAllWindows()
print("프로그램 종료.")
