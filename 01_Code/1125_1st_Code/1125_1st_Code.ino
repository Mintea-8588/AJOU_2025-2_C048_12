// 현재 구동: 초음파, 서보, DC 모터 - 라인트래킹, 카메라는 아직 미구현

// 서보 모터
#include "Servo.h"
Servo servo1;
#define servo_motor 2

// 우측 DC모터
#define ENA 3
#define IN1 4
#define IN2 5

// 좌측 DC모터
#define ENB 11
#define IN3 13
#define IN4 12

// 초음파 센서
#define TRIG 7
#define ECHO 6

// 기타 기호 상수 정의
#define SPEED_MAX 255
#define DISTANCE_THRESHOLD 30
#define TURN_TIME 500

void setup()
{
  Serial.begin(9600);

  pinMode(ENA, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);

  pinMode(ENB, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);

  servo1.attach(servo_motor);
  servo1.write(90);
  delay(100);

  pinMode(TRIG, OUTPUT);
  pinMode(ECHO, OUTPUT);
}

long getDistance()
{
  float duration = 0; // 초음파가 갔다가 돌아오는 시간을 저장
  float distance = 0; // 센서-물체 사이 거리를 저장

  digitalWrite(TRIG, LOW); // TRIG HIGH,LOW 상태초기화
  delayMicroseconds(2); // 초기화 이후 적당한 딜레이를 줘서 안정화

  digitalWrite(TRIG, HIGH);
  delayMicroseconds(10); // 10 마이크로초동안 HIGH 신호 -> 초음파 생성

  digitalWrite(TRIG, LOW);
  duration = pulseIn(ECHO, HIGH); // ECHO가 HIGH->LOW 되는 시간 저장
  
  distance = duration * 343 / 20000;
  return distance;
}

void moveForward()
{
  // 우측 모터 정회전
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);

  // 좌측 모터 정회전
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);

  // 모터 활성화, 속도 설정
  analogWrite(ENA, SPEED_MAX);
  analogWrite(ENB, SPEED_MAX);
}

void moveBackward()
{
  // 우측 모터 역회전
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);

  // 좌측 모터 역회전
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);

  // 모터 활성화, 속도 설정
  analogWrite(ENA, SPEED_MAX);
  analogWrite(ENB, SPEED_MAX);
}

void stopMotors()
{
  // 우측 모터 정지
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, HIGH);

  // 좌측 모터 정지
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, HIGH);

  // 전류 차단
  analogWrite(ENA, 0);
  analogWrite(ENB, 0);
}

void turnLeft()
{
  // 우측 모터 정회전
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);

  // 좌측 모터 역회전
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);

  // 모터 활성화, 속도 설정
  analogWrite(ENA, SPEED_MAX);
  analogWrite(ENB, SPEED_MAX);
}

void turnRight()
{
  // 우측 모터 역회전
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);

  // 좌측 모터 정회전
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);

  // 모터 활성화, 속도 설정
  analogWrite(ENA, SPEED_MAX);
  analogWrite(ENB, SPEED_MAX);
}

void loop()
{
  moveForward();

  long distance = getDistance();
  Serial.print("Distance: ");
  Serial.print(distance);
  Serial.println(" cm");

  if (distance > 0 && distance <= DISTANCE_THRESHOLD)
  {
    stopMotors();
    Serial.println("장애물을 발견했습니다. 좌회전을 시도합니다.");
    delay(200);

    Serial.println("좌회전을 시도 중입니다.");
    turnLeft();
    delay(TURN_TIME);
    stopMotors();
    delay(200);
  }
}
