const int IR_PIN = A2;

void setup() {
  Serial.begin(9600);
  pinMode(IR_PIN, INPUT);
  pinMode(LED_BUILTIN, OUTPUT);
}

void loop() {
  int val = digitalRead(IR_PIN);

  if (val == 0) {
    Serial.println("obstacle=yes");
    digitalWrite(LED_BUILTIN, HIGH);
  } else {
    Serial.println("obstacle=no");
    digitalWrite(LED_BUILTIN, LOW);
  }

  delay(500);
}
