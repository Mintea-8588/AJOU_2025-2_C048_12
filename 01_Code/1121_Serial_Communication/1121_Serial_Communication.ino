char cmd;

void setup()
{
  Serial.begin(9600);
}

void loop()
{
  if(Serial.available())
  {
    cmd = Serial.read();
    if(cmd=='a')
    {
      Serial.println("아두이노: a");
      delay(100);
    }
    else if(cmd=='b')
    {
      Serial.println("아두이노: b");
      delay(100);
    }
  }
}

