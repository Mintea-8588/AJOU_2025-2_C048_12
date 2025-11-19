
// 우측 DC 모터 (MOTOR A)
#define ENA 5    // 아두이노 디지털 5번 핀 (속도/활성화 제어)
#define IN1 4    // 아두이노 디지털 4번 핀 (방향 제어)
#define IN2 3    // 아두이노 디지털 3번 핀 (방향 제어)

// 좌측 DC 모터 (MOTOR B) - L298N 핀 번호 및 연결에 대한 일반적인 가정
#define ENB 6    // 아두이노 디지털 6번 핀 (속도/활성화 제어) - ENA와 다르게 임의 설정
#define IN3 7    // 아두이노 디지털 7번 핀 (방향 제어)
#define IN4 8    // 아두이노 디지털 8번 핀 (방향 제어)


// 속도 설정 (0~255) 
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
  // 우측 모터 (MOTOR A) 정회전 
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  
  // 좌측 모터 (MOTOR B) 정회전
  digitalWrite(IN3, HIGH); 
  digitalWrite(IN4, LOW);

  // ENA/ENB 핀을 통해 모터 활성화 및 속도 설정
  analogWrite(ENA, SPEED_MAX);
  analogWrite(ENB, SPEED_MAX);
}

void moveBackward()
{
  // 우측 모터 (MOTOR A) 역회전 
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  
  // 좌측 모터 (MOTOR B) 역회전
  digitalWrite(IN3, LOW); 
  digitalWrite(IN4, HIGH);

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

  // ENA/ENB 핀을 최저치로 설저하여 전류를 차단 (과열 방지
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
  moveForward(); // 1초간 (좌)정회전, (우)정회전
  delay(1000);
  stopMotors(); // 1초간 정지
  delay(1000);

  moveBackward(); // 1초간 (좌)역회전, (우)역회전
  delay(2000);
  stopMotors(); // 1초간 정지
  delay(1000);

  turnLeft(); // 1초간 (좌)정회전, (우)역회전
  delay(3000);
  stopMotors(); // 1초간 정지'
  delay(1000);

  turnRight(); // 1초간 (좌)역회전, (우)정회전
  delay(4000);
  stopMotors(); // 1초간 정지
  delay(1000);
}