#include "Servo.h" // 서보모터를 사용하기 위한 헤더파일 호출
Servo servo1; // 서보모터 객체 선언
#define servo_motor 2 // 서보모터 Signal 핀, 아두이노 우노 보드 디지털 3번 핀에 연결

void setup() // 초기화
{
Serial.begin(9600); // 통신속도 설정
servo1.attach(servo_motor); // 서보모터 핀 설정
servo1.write(90); // 서보모터 초기값 90도 설정
Serial.println("Please Select the degree of Servo1");
Serial.println("(1)30 (2)60 (3)90 (4)120 (5)150");
}

void loop() // 무한루프
{
  if (Serial.available()) 
  { // 시리얼통신 입력 대기 
    char data = Serial.read(); // 입력 받은 값을 변수에 저장
    switch (data) 
    {
      case '1': servo1.write(30); Serial.write("30 degree\n"); break; // "1"을 입력받았을때 30도
      case '2': servo1.write(60); Serial.write("60 degree\n"); break; // "2"를 입력받았을때 60도
      case '3': servo1.write(90); Serial.write("90 degree\n"); break; // "3"을 입력받았을때 90도
      case '4': servo1.write(120); Serial.write("120 degree\n"); break; // "4"를 입력받았을때 120도
      case '5': servo1.write(150); Serial.write("150 degree\n"); break; // "5"를 입력받았을때 150도
      default: Serial.println("Please, Write 1 ~ 5 !!"); break; // 1~5 이외의 값을 받았을 때 문자 출력
   }
  }
}