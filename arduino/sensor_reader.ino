#include <DHT.h>

#define DHTPIN 8
#define DHTTYPE DHT11
#define SOIL_PIN A0

const int sen_max = 570;
const int sen_min = 246;

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(115200);  // Match with Flask's serial port baud rate
  dht.begin();
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();  // remove \r\n

    if (command == "read") {
      int rawSoil = analogRead(SOIL_PIN);
      float soilMoisturePercent = map(rawSoil, sen_max, sen_min, 0.0, 100.0);

      // Clamp moisture to [0, 100]
      if (soilMoisturePercent < 0) soilMoisturePercent = 0;
      if (soilMoisturePercent > 100) soilMoisturePercent = 100;

      float humidity = dht.readHumidity();
      float temperature = dht.readTemperature();

      // Fallback values in case of read failure
      if (isnan(humidity)) humidity = 0.0;
      if (isnan(temperature)) temperature = 0.0;

      // Output: sensor_value,temperature,humidity
      Serial.print(soilMoisturePercent, 1);
      Serial.print(",");
      Serial.print(temperature, 1);
      Serial.print(",");
      Serial.println(humidity, 1);

      Serial.flush();  // Ensure data is sent before next read
    }
  }
}
