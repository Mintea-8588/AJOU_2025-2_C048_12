// 현재 구동: 초음파, 서보, DC 모터, 라인트래킹, 카메라-딥러닝 통신

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

// 적외선(라인트래킹) 센서
#define SENSOR1 10 // 좌측
#define SENSOR2 9 // 중앙
#define SENSOR3 8 // 우측

// 초음파 센서
#define TRIG 7
#define ECHO 6

// 기타 기호 상수 정의
#define SPEED_MAX 220
#define DISTANCE_CAM_START 18
#define DISTANCE_CAM_BOUNDARY 15
#define DISTANCE_THRESHOLD 15
#define TURN_TIME 1200
#define CAM 5

bool decisionMode = false;
char decidedDirection = 'N';

void setup()
{
  Serial.begin(9600); // 시리얼 통신 속도

  // DC 모터
  pinMode(ENA, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);

  pinMode(ENB, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);

  // 초음파 센서
  pinMode(TRIG, OUTPUT);
  pinMode(ECHO, INPUT);

  // 라인트래킹 센서(적외선)
  pinMode(SENSOR1, INPUT);
  pinMode(SENSOR2, INPUT);
  pinMode(SENSOR3, INPUT);

  // 서보 모터
  servo1.attach(servo_motor);
  servo1.write(90);
  delay(100);
}

// 거리 계산 함수
long getDistance()
{
  long duration = 0; // 초음파가 갔다가 돌아오는 시간을 저장
  float distance = 0; // 센서-물체 사이 거리를 저장

  digitalWrite(TRIG, LOW); // TRIG HIGH,LOW 상태초기화
  delayMicroseconds(2); // 초기화 이후 적당한 딜레이를 줘서 안정화

  digitalWrite(TRIG, HIGH);
  delayMicroseconds(10); // 10 마이크로초동안 HIGH 신호 -> 초음파 생성

  digitalWrite(TRIG, LOW);
  duration = pulseIn(ECHO, HIGH); // ECHO가 HIGH->LOW 되는 시간 저장
  
  distance = duration * 343.0 / 20000.0; // 측정한 시간을 cm 단위의 거리로 변환
  return (long)distance; // 거리값을 반환
}

// 자동차 구동 함수
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

  // 좌측 모터 정지
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, HIGH);

  // 모터 활성화, 속도 설정
  analogWrite(ENA, SPEED_MAX);
  analogWrite(ENB, SPEED_MAX);
}

void turnRight()
{
  // 우측 모터 정지
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, HIGH);

  // 좌측 모터 정회전
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);

  // 모터 활성화, 속도 설정
  analogWrite(ENA, SPEED_MAX);
  analogWrite(ENB, SPEED_MAX);
}

void turnLeft_1()
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

void turnLeft_1()
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

// 자세 제어 함수
void leftSensorWarning()
{
  Serial.println("자동차가 좌측 실선을 밟았습니다. 정상 경로 복구를 시도합니다.");
  stopMotors();
  delay(500);

  moveBackward(); // 뒤로 후진
  delay(300);
  stopMotors(); 
  delay(500);

  turnRight_1(); // 제자리에서 오른쪽으로 회전 (정방향)
  delay(450);
  stopMotors();
  delay(500);

  Serial.println("복구 로직 실행을 완료하였습니다. 경로 주행을 재개합니다.");
  moveForward();
}

void rightSensorWarning()
{
  Serial.println("자동차가 우측 실선을 밟았습니다. 정상 경로 복구를 시도합니다.");
  stopMotors();
  delay(500);

  moveBackward(); // 뒤로 후진
  delay(300);
  stopMotors(); // 제자리에서 왼쪽으로 회전 (정방향)
  delay(500);

  turnLeft_1();
  delay(450);
  stopMotors();
  delay(500);

  Serial.println("복구 로직 실행을 완료하였습니다. 경로 주행을 재개합니다.");
  moveForward();
}

char requestOneSample()
{
  Serial.println("SNAP"); // 문자열 출력 -> Python이 캡처를 하도록 신호 보냄
  unsigned long startTime= millis(); // 현재 시간을 밀리초 단위로 기록
  while (Serial.available() == 0) // 데이터 수신이 되지 않고
  {
    if (millis() - startTime > 3000) // 이것이 3초 동안 지속될 때
    {
      return 'N'; // N(negative) 반환 (예외)
    }
  }
  char cmd = Serial.read(); // 데이터가 도착하면 시리얼 버퍼에서 첫번째 문자를 읽어 변수에 저장
  while (Serial.available() > 0) 
  {
    Serial.read(); // 한 번 더 읽음 (저장할 변수가 없으므로 버퍼가 비워짐)
  }

  return cmd; // cmd에 저장된 신호(L/R/N) 반환
}

char makeCameraDecision()
{
  Serial.println("--- 카메라 측정 시작 ---");

  int leftCount = 0;
  int rightCount = 0;

  // 1단계: 5회 샘플링
  for (int i=0 ; i<CAM ; i++)
  {
    char result = requestOneSample(); // Python으로부터 받은 시그널 입력
    if (result == 'L') // 받은 시그널이 Left이면
    {
      leftCount++; // 왼쪽 카운트 1 증가
    }
    else if (result == 'R') // 받은 시그널이 Right이면
    {
      rightCount++; // 오른쪽 카운트 1 증가
    }
    delay(50);
  }

  // 2단계: 동률 시 추가 샘플링
  while (leftCount == rightCount)
  {
    Serial.println("판단 근거가 부족하여 추가 샘플링을 진행합니다.");
    char extra = requestOneSample();
    if (extra == 'L')
    {
      leftCount++;
    }
    else if (extra == 'R')
    {
      rightCount++;
    }
    delay(50);
  }

  // 3단계 방향 결정 (회전은 하지 않음)
  char finalDecision = 'N';
  if (leftCount > rightCount)
  {
    Serial.println("판단 결과: 좌회전");
    finalDecision = 'L';
  }
  else
  {
    Serial.println("판단 결과: 우회전");
    finalDecision = 'R';
  }

  Serial.println("--- 카메라 측정 완료, 회전 위치까지 이동합니다. ---");
  return finalDecision;
}

void loop()
{
  int s1 = digitalRead(SENSOR1); // 좌측 센서 라인 감지 (흑: 0, 백: 1)
  int s2 = digitalRead(SENSOR2); // 중앙 센서 라인 감지 (흑: 0, 백: 1)
  int s3 = digitalRead(SENSOR3); // 우측 센서 라인 감지 (흑: 0, 백: 1)

  long distance = getDistance();

  // 첫 번째 경우: 카메라 판단이 완료되었고, 거리가 12cm 이하일 때 -> 회전 수행
  if (decisionMode && distance > 0 && distance <= DISTANCE_THRESHOLD)
  {
    stopMotors();
    Serial.println("장애물을 발견했습니다. 회전을 시도합니다.");
    delay(100);

    if (decidedDirection == 'L')
    {
      Serial.println("좌회전이 진행 중입니다.");
      turnLeft();
      delay(TURN_TIME);
    }
    else if (decidedDirection == 'R')
    {
      Serial.println("우회전이 진행 중입니다.");
      turnRight();
      delay(TURN_TIME);
    }
    stopMotors();
    delay(500);

    // 변수 초기화
    decisionMode = false;
    decidedDirection = 'N';
  }

  // 두 번째 경우: 카메라 판단 전, 길이가 21cm 이하일 때 -> 카메라 기능 수행
  if (!decisionMode && distance > 0 && distance <= DISTANCE_CAM_START)
  {
    stopMotors();
    delay(300);

    long distance_before_cam = getDistance(); 
    Serial.print("판단 전 재측정 거리: ");
    Serial.println(distance_before_cam);
    delay(300);

    if (distance_before_cam > DISTANCE_CAM_START) // (1) 너무 멀 때 (21cm 초과)
    {
        Serial.println("거리가 너무 멀어 직진을 재개합니다.");
        moveForward();
    }

    else if (distance_before_cam <= DISTANCE_CAM_BOUNDARY) // (2) 너무 가까울 때 (18cm 이하)
    {
        // 정지했으나 너무 가깝다면 후진하여 거리를 벌립니다.
        Serial.println("거리가 너무 가까워 후진하여 거리를 벌립니다.");
        moveBackward();
        delay(100); // 잠시 후진
        stopMotors();
        // 후진 후 다시 루프 처음으로 돌아가 새로운 거리 측정 및 판단을 시도
    }

    else // (3) 최적 인식 구간일 때 
    {
        Serial.println("최적 인식 구간입니다. 카메라 판단을 수행합니다.");
        
        decidedDirection = makeCameraDecision();
        decisionMode = true; // 판단 완료 신호

        moveForward(); // 판단 후 주행 재개
    }
  }

  // 나머지 일반적인 경우: 라인트래킹 및 직진
  if (s1 == LOW && s3 == HIGH) // 자동차가 왼쪽 실선에 닿았을 때
  {
    leftSensorWarning();
  }
  else if (s3 == LOW && s1 == HIGH) // 자동차가 오른쪽 실선에 닿았을 때
  {
    rightSensorWarning();
  }
  else // 기타 정상 상태일 때
  {
    moveForward();
  }

}
