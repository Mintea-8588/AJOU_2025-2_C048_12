#define EA 5 // 모터드라이버 EA 핀, 아두이노 우노 보드 디지털 5번 핀에 연결
#define M_IN1 4 // 모터드라이버 IN1 핀, 아두이노 우노 보드 디지털 4번 핀에 연결
#define M_IN2 3 // 모터드라이버 IN2 핀, 아두이노 우노 보드 디지털 3번 핀에 연결
int motorA_vector = 1; // DC모터의 회전방향이 반대일 시 1을 0으로
// "1"을 "0"으로 바꿔주면 DC모터의 회전방향이 바뀜.

void setup() {
pinMode(EA, OUTPUT); // EA와 연결된 핀 출력 설정
pinMode(M_IN1, OUTPUT); // IN1과 연결된 핀 출력 설정
pinMode(M_IN2, OUTPUT); // IN2와 연결된 핀 출력 설정
}

void loop() {
// DC모터 정회전
digitalWrite(EA, HIGH); // 모터구동 ON
digitalWrite(M_IN1, motorA_vector); // IN1에 HIGH(or LOW)
digitalWrite(M_IN2, !motorA_vector); // IN2에 LOW(or HIGH)
delay(5000); // 5초간 지연

// DC모터 정지
digitalWrite(EA, LOW); // 모터구동 OFF
digitalWrite(M_IN1, LOW); // IN1에 LOW
digitalWrite(M_IN2, LOW); // IN2에 LOW
delay(5000); // 5초간 지연

// DC모터 역회전
digitalWrite(EA, HIGH); // 모터구동 ON
digitalWrite(M_IN1, !motorA_vector); // IN1에 LOW(or HIGH)
digitalWrite(M_IN2, motorA_vector); // IN2에 HIGH(or LOW)
delay(5000); // 5
}