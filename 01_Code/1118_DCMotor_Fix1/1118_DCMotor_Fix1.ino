// 한 쪽 모터의 정회전·역회전 확인 (별도 함수 만들어 호출하는 방식)

#define ENA 5
#define IN1 4
#define IN2 3

const int SPEED_MAX = 200;

void setup()
{
  pinMode(ENA, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
}

void moveForward()
{
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  analogWrite(ENA, SPEED_MAX);
  delay(1000);
}

void moveBackward()
{
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  analogWrite(ENA, SPEED_MAX);
  delay(1000);
}

void stop()
{
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, HIGH);
  analogWrite(ENA, SPEED_MAX);
  delay(1000);
}

void loop()
{
  moveForward();
  stop();
  moveBackward();
  stop();
}

