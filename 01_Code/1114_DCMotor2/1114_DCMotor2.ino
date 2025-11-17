#define EA 5 // 모터드라이버 EA 핀, 아두이노 우노 보드 디지털 5번 핀에 연결
#define M_IN1 4 // 모터드라이버 IN1 핀, 아두이노 우노 보드 디지털 4번 핀에 연결
#define M_IN2 3 // 모터드라이버 IN2 핀, 아두이노 우노 보드 디지털 3번 핀에 연결

void setup() 
{
  pinMode(EA, OUTPUT); // EA와 연결된 핀 출력 설정
  pinMode(M_IN1, OUTPUT); // IN1과 연결된 핀 출력 설정
  pinMode(M_IN2, OUTPUT); // IN2와 연결된 핀 출력 설정
}

void loop( ) 
{
  // DC모터 정회전
  digitalWrite(M_IN1, 1); // IN1에 HIGH
  digitalWrite(M_IN2, 0); // IN2에 LOW

  // for 문을 이용하여 +10씩 점점 증가시켜 값을 입력
  for (int i = 10 ; i < 255 ; i = i+10) // 0~250으로 설정, 주기는 0.3 * 26 = 7.8초
  {
    analogWrite(EA, i); // 아날로그 신호의 세기를 i에 따라 설정
    delay(300); // 0.3초 단위로 i를 10씩 증가시킴
  }

}