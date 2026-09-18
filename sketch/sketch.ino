#include <Arduino_RouterBridge.h>

void setup() {
  Serial.begin(9600); // Inicializa el puerto serie a 9600 baudios
}

void loop() {
  // Read Potentiometer 1 (Discard first read, keep second)
  analogRead(A0); 
  delay(10);
  int potRed = analogRead(A0);

  // Read Potentiometer 2 (Discard first read, keep second)
  analogRead(A1); 
  delay(10);
  int potBlue = analogRead(A1);

  // Print results
  Serial.print("Pot red: "); Serial.print(potRed);
  Serial.print(" | Pot blue: "); Serial.println(potBlue);
  delay(100);

  Bridge.call("receive_potValues", potRed, potBlue);
}
