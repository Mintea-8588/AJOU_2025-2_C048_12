
// 우측 DC 모터 (MOTOR A)
#define ENA 5    // 아두이노 디지털 5번 핀 (속도/활성화 제어)
#define IN1 4    // 아두이노 디지털 4번 핀 (방향 제어)
#define IN2 3    // 아두이노 디지털 3번 핀 (방향 제어)

// 좌측 DC 모터 (MOTOR B) - L298N 핀 번호 및 연결에 대한 일반적인 가정
// 강의노트에 좌측 모터 핀 정의가 명시되지 않아, 일반적인 L298N 연결에 따라 IN3/IN4를 7번/8번으로 가정함.
#define ENB 6    // 아두이노 디지털 6번 핀 (속도/활성화 제어) - ENA와 다르게 임의 설정
#define IN3 7    // 아두이노 디지털 7번 핀 (방향 제어)
#define IN4 8    // 아두이노 디지털 8번 핀 (방향 제어)


// 속도 설정 (0~255) - 최대 속도로 동작하도록 255로 설정
const int SPEED_MAX = 255;


void setup() 
{
  // 모터 제어 핀을 출력으로 설정
  pinMode(ENA, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  
  pinMode(ENB, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
}


// --- 모터 제어 함수 정의 ---

void moveForward() 
{
  // 우측 모터 (MOTOR A) 정회전 (Page 12: HIGH, LOW)
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  
  // 좌측 모터 (MOTOR B) 정회전
  digitalWrite(IN3, HIGH); 
  digitalWrite(IN4, LOW);

  // ENA/ENB 핀을 통해 모터 활성화 및 속도 설정
  analogWrite(ENA, SPEED_MAX);
  analogWrite(ENB, SPEED_MAX);
}

// 정지 = 우측 정지 + 좌측 정지 
void stopMotors() 
{
  // 모터 방향 핀을 모두 HIGH로 설정하여 정지 (제동)
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, HIGH);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, HIGH);

  // ENA/ENB 핀을 LOW로 설정하여 모터 비활성화 (전류 차단) 
  analogWrite(ENA, 0);
  analogWrite(ENB, 0);
}

// 좌회전 = 우측 정회전 + 좌측 역회전 
void turnLeft() 
{
  // 우측 모터 (MOTOR A) 정회전 
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  
  // 좌측 모터 (MOTOR B) 역회전 
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);

  // ENA/ENB 핀을 통해 모터 활성화 및 속도 설정
  analogWrite(ENA, SPEED_MAX);
  analogWrite(ENB, SPEED_MAX);
}

// 우회전 = 우측 역회전 + 좌측 정회전 
void turnRight() 
{
  // 우측 모터 (MOTOR A) 역회전 
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  
  // 좌측 모터 (MOTOR B) 정회전
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);

  // ENA/ENB 핀을 통해 모터 활성화 및 속도 설정
  analogWrite(ENA, SPEED_MAX);
  analogWrite(ENB, SPEED_MAX);
}

// Test Move (경우에 따라 수정하기)
void loop() 
{
  // 1. 5초 동안 전진
  moveForward();
  delay(5000); 

  // 짧은 정지 (관성 제거)
  stopMotors();
  delay(500); 

  // 2. 3초 동안 좌회전
  turnLeft();
  delay(3000); 

  // 짧은 정지 (관성 제거)
  stopMotors();
  delay(500); 
  
  // 3. 5초 동안 전진
  moveForward();
  delay(5000); 

  // 짧은 정지 (관성 제거)
  stopMotors();
  delay(500);

  // 4. 3초 동안 우회전
  turnRight();
  delay(3000); 

  // 짧은 정지 (관성 제거)
  stopMotors();
  delay(500); 

  // 5. 5초 동안 전진
  moveForward();
  delay(5000); 

  // 최종 정지 후 반복하지 않도록 무한 루프 진입
  stopMotors();
  while(true);
}