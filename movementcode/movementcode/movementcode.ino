#define MQ7_PIN A0   // only analog pin on ESP8266

void setup() {
  Serial.begin(115200);
}

void loop() {
  int co = analogRead(MQ7_PIN);

  Serial.print("CO level: ");
  Serial.println(co);

  delay(1000);
}