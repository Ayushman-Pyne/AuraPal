---
cssclasses:
  - center-images
---

## Connections
- [[SG90]]
- [[TTP223]]
- [[ESP32-S3-N16R8]]

## *HOW TO RUN?*
- upload and run ESP with `platformio.ini` and `main.cpp`

## *Codes*
### ***platformio.ini***
```ini
[env:esp32-s3-devkitc-1]
platform = espressif32
board = esp32-s3-devkitc-1
framework = arduino
monitor_speed = 115200

lib_deps =
    madhephaestus/ESP32Servo
```

### ***main.cpp***
```C++
#include <Arduino.h>
#include <ESP32Servo.h>

// Pins
#define SERVO_PIN 47
#define TOUCH_PIN 14

Servo myServo;

// State tracking
bool lastTouchState = LOW;
bool servoState = false; // false = 0°, true = 90°

void setup() {
    Serial.begin(115200);

    pinMode(TOUCH_PIN, INPUT);

    myServo.attach(SERVO_PIN);
    myServo.write(0);

    Serial.println("Ready...");
}

void loop() {
    bool touchState = digitalRead(TOUCH_PIN);

    // Detect rising edge (when you touch it)
    if (touchState == HIGH && lastTouchState == LOW) {
        Serial.println("Touched!");

        // Toggle servo position
        servoState = !servoState;

        if (servoState) {
            myServo.write(180);
        } else {
            myServo.write(0);
        }

        delay(200); // debounce
    }

    lastTouchState = touchState;

    delay(20);
}
```
