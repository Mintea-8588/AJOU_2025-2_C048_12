#define TRIG 7
#define ECHO 6

void setup(){
Serial.begin(9600);
pinMode (TRIG, OUTPUT);
pinMode (ECHO, INPUT);
}

void loop(){
float duration = 0; // 초음파가 갔다가 돌아오는 시간을 저장
float distance = 0; // 센서-물체 사이 거리를 저장
digitalWrite(TRIG, LOW); // TRIG HIGH,LOW 상태초기화
delayMicroseconds(2); // 초기화 이후 적당한 딜레이를 줘서 안정화
digitalWrite(TRIG, HIGH);
delayMicroseconds(10); // 10 마이크로초동안 HIGH 신호 -> 초음파 생성
digitalWrite(TRIG, LOW);
duration = pulseIn(ECHO, HIGH); // ECHO가 HIGH->LOW 되는 시간 저장
distance = duration * 343 / 20000 ;
Serial.print(distance);
Serial.println(" Cm");
delay(1000);
}