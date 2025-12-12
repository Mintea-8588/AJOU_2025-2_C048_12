import cv2
import numpy as np
from PIL import Image
import os
import sys

# --- 설정 (이전과 동일) ---
TARGET_SIZE = 64
TEMPLATE_FILENAME = f"templates_{TARGET_SIZE}x{TARGET_SIZE}.npy"
DISTANCE_THRESHOLD = 600 
SAMPLING_COUNT = 100 

# --- 초기화 (이전과 동일) ---
try:
    TEMPLATES = np.load(TEMPLATE_FILENAME)
    if TEMPLATES.shape != (10, TARGET_SIZE, TARGET_SIZE):
        raise ValueError(f"템플릿 크기 오류: {TEMPLATES.shape}가 (10, {TARGET_SIZE}, {TARGET_SIZE})이 아닙니다.")
    print(f"✅ 템플릿 파일 ({TEMPLATE_FILENAME}) 로드 완료.")
except FileNotFoundError:
    print(f"❌ 템플릿 파일 '{TEMPLATE_FILENAME}'을 찾을 수 없습니다.")
    sys.exit()

video = cv2.VideoCapture(0)
if not video.isOpened():
    print("❌ 카메라를 열 수 없습니다.")
    sys.exit()

# --- 비율 유지 및 자동 크롭 전처리 함수 (유지) ---
# ... (preprocess_image_with_padding 함수 정의 유지) ...

# --- 비율 유지 및 자동 크롭 전처리 함수 (유지) ---
def preprocess_image_with_padding(frame, target_size):
    """
    원본 이미지에서 흰색 글씨 영역을 자동으로 크롭하고, 
    종횡비를 유지하며 Target Size 크기의 캔버스에 패딩합니다.
    """
    img = Image.fromarray(frame, 'RGB').convert('L')
    img_np = np.array(img)
    
    _, thresh = cv2.threshold(img_np, 50, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)
        
        margin = 10
        x_start = max(0, x - margin)
        y_start = max(0, y - margin)
        x_end = min(img_np.shape[1], x + w + margin)
        y_end = min(img_np.shape[0], y + h + margin)

        img = img.crop((x_start, y_start, x_end, y_end))
    
    W, H = img.size
    
    if W > H:
        new_W = target_size
        new_H = int(H * target_size / W)
    else:
        new_H = target_size
        new_W = int(W * target_size / H)
        
    resized_img = img.resize((new_W, new_H), Image.LANCZOS)

    final_img = Image.new('L', (target_size, target_size), 0)
    
    x_offset = (target_size - new_W) // 2
    y_offset = (target_size - new_H) // 2
    final_img.paste(resized_img, (x_offset, y_offset))

    im2_array = np.array(final_img, dtype=np.float32)
    current_image = im2_array / 255.0
    
    return current_image

# --- 좌회전/우회전 숫자 입력 함수 (유지) ---
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
print("\n설정 완료! 예측 대기 중...\n")

# --- 유틸리티 함수 ---
def get_action(digit):
    """숫자에 해당하는 명령(L/R/N)을 반환합니다."""
    if digit in L_LIST:
        return 'L'
    if digit in R_LIST:
        return 'R'
    return 'N'


# --- 메인 루프 (실시간 출력 및 주기적 예측) ---

print("\n--- 실시간 템플릿 매칭 인식 시작 (종료: 'q' 키) ---")
print(f"    (최빈값 업데이트 주기: {SAMPLING_COUNT} 프레임)")
print(f"    (거리 임계값: {DISTANCE_THRESHOLD})")
print("--------------------------------------------------\n")

# 예측 결과를 저장할 변수 초기화
prediction_history = []
distance_history = []
frame_counter = 0

# 화면에 표시될 최종 결과값 초기값
display_cmd = "N (Neutral)"
display_distance = "N/A"
display_color = (255, 255, 255) # White
mode_1st_log = -1
mode_2nd_log = -1

while True:
    ret, frame = video.read()
    if not ret: break
    
    # 1. 전처리 및 템플릿 매칭 (매 프레임마다)
    current_image = preprocess_image_with_padding(frame, TARGET_SIZE)
    min_distance = float('inf')
    predicted_digit = -1
    
    for digit in range(10):
        template = TEMPLATES[digit]
        distance = np.sum((current_image - template) ** 2)
        if distance < min_distance:
            min_distance = distance
            predicted_digit = digit

    # 2. 데이터 누적
    prediction_history.append(predicted_digit)
    distance_history.append(min_distance)
    frame_counter += 1

    # 3. 주기적 업데이트 (100 프레임 도달 시)
    if frame_counter >= SAMPLING_COUNT:
        
        all_predictions_array = np.array(prediction_history)
        all_distances_array = np.array(distance_history)
        
        # 3-1. 1순위와 2순위 최빈값 계산
        unique_elements, counts = np.unique(all_predictions_array, return_counts=True)
        sorted_indices = np.argsort(counts)[::-1] 
        
        mode_1st = unique_elements[sorted_indices[0]]
        mode_2nd = unique_elements[sorted_indices[1]] if len(sorted_indices) > 1 else -1
        
        # 3-2. 1순위 최빈값의 평균 거리 계산
        mode_1st_indices = np.where(all_predictions_array == mode_1st)[0]
        mode_1st_distances = all_distances_array[mode_1st_indices]
        final_avg_distance = np.mean(mode_1st_distances)
        
        
        # --- 3-3. 결정 논리 및 화면 표시 결과 업데이트 ---
        
        # 1순위와 2순위의 명령을 미리 정의 (오류 방지)
        action_1st = get_action(mode_1st)
        action_2nd = get_action(mode_2nd)
        
        # 1순위와 2순위를 로그에 저장 (오류 방지)
        mode_1st_log = mode_1st
        mode_2nd_log = mode_2nd

        if final_avg_distance <= DISTANCE_THRESHOLD:
            
            # 결정 논리: 1순위 명령 우선
            if action_1st != 'N':
                final_cmd = f"L ({mode_1st})" if action_1st == 'L' else f"R ({mode_1st})"
                final_color = (0, 255, 0) # Green (1순위)
            elif action_2nd != 'N':
                final_cmd = f"L ({mode_2nd})" if action_2nd == 'L' else f"R ({mode_2nd})"
                final_color = (255, 255, 0) # Yellow (2순위)
            else:
                final_cmd = f"N (Unassigned: {mode_1st})"
                final_color = (150, 150, 150) # Gray
            
        else:
            final_cmd = f"None (Dist > {DISTANCE_THRESHOLD})"
            final_color = (0, 0, 255) # Red

        # 최종 화면 출력 변수 업데이트
        display_cmd = final_cmd
        display_distance = f"{final_avg_distance:.2f}"
        display_color = final_color
        
        # 3-4. 콘솔 출력 (오류 발생 지점 수정 완료)
        print(f"[{SAMPLING_COUNT}f Update] 1순위: {mode_1st} ({action_1st}), 2순위: {mode_2nd} ({action_2nd}) -> 최종 명령: {final_cmd}")
        print(f"  -> 1순위 평균 유사도: {display_distance}")


        # 3-5. 카운터 및 히스토리 초기화
        frame_counter = 0
        prediction_history = []
        distance_history = []
        
    # 4. 실시간 출력
    cv2.putText(frame, f"Command: {display_cmd}", (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, display_color, 2)
    cv2.putText(frame, f"Avg Dist (1st): {display_distance}", (10, 70), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, display_color, 2)
    cv2.putText(frame, f"Frame Count: {frame_counter}/{SAMPLING_COUNT}", (10, 110), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
    
    cv2.imshow('Camera Input (Press q to quit)', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# --- 종료 및 정리 ---
video.release()
cv2.destroyAllWindows()
print("\n프로그램 종료.")
