#define SENSOR 8 // 디지털 핀번호를 8번으로 설정

void setup()
{
  Serial.begin(9600); // 시리얼 통신 속도를 9600bps로 설정
  pinMode(SENSOR, INPUT); // 기호 상수로 정의한 핀번호에 해당하는 핀을 입력 모드로 설정
}

void loop()
{
  if (digitalRead(SENSOR)) // 함수 호출과 동시에 if문 판단 (digital 신호가 1이면) 

  {
    Serial.println("BLACK"); // 검정색
  }

  else // 아니면 (0이면)
  {
    Serial.println("WHITE"); // 흰색
  }
  delay(1000); // 1초마다 흑백 여부 판단 
}

