#include "SoftwareSerial.h"
SoftwareSerial serial_connection(10, 11); //Create a serial connection with TX and RX on these pins
#define IN1 7
#define IN2 6
#define IN3 5
#define IN4 4
#define MAX_SPEED 255 //từ 0-255
#define MIN_SPEED 0
byte blue = 0;
byte temp = 10;
void setup()
{
  Serial.begin(9600);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  pinMode(9, OUTPUT);
  pinMode(3, OUTPUT);
  pinMode(2, INPUT);
  serial_connection.begin(9600); //Initialize communications with the bluetooth module
  Serial.println("Started");     //Tell the serial monitor that the sketch has started.
}

void DungLai()
{
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
}
void QuayPhai()
{
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
  //quay
  delay(1000);
  digitalWrite(IN2, HIGH);
  analogWrite(9, 100);
  delay(1000);
  digitalWrite(IN2, LOW);
}
void QuayTrai()
{
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
  //quay
  delay(1000);
  digitalWrite(IN3, HIGH);
  analogWrite(3, 100);
  delay(1000);
  digitalWrite(IN3, LOW);
}
void DiThang()
{
  digitalWrite(IN1, LOW); // chân này không có PWM
  digitalWrite(IN2, HIGH);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
  analogWrite(9, 100);
  analogWrite(3, 100);
}
void SangPhai()
{
  digitalWrite(IN1, LOW); // chân này không có PWM
  digitalWrite(IN2, HIGH);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
  delay(200);
  digitalWrite(IN3, HIGH);
}
void SangTrai()
{
  digitalWrite(IN1, LOW); // chân này không có PWM
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
  delay(200);
  digitalWrite(IN2, HIGH);
}
void loop()
{
  byte byte_count = serial_connection.available();

  if (serial_connection.available() > 0)
  {
    blue = serial_connection.read(); // đọc dữ liệu đưa về từ hc-05
    serial_connection.println(blue);
    Serial.println(blue);
  }
  if (temp != blue)
  {
    temp = blue;
    if (blue == 'A')
    {
      DiThang();
    }
    if (blue == 'B')
    {
      DungLai();
    }
    if (blue == 'C')
    {
      QuayTrai();
    }
    if (blue == 'D')
    {
      QuayPhai();
    }
    if (blue == 'E')
    {
      SangTrai();
    }
    if (blue == 'F')
    {
      SangPhai();
    }
  }
}