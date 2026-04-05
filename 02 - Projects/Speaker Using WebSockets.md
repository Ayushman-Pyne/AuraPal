---
cssclasses:
  - center-images
---

## Connections
- [[MAX98357A]]
- [[ESP32-S3-N16R8]]

## *HOW TO RUN?*
- Setup venv and install websockets using `pip install websockets`


## *Codes*
### ***platformio.ini***
```ini
[env:4d_systems_esp32s3_gen4_r8n16]
platform = espressif32
board = 4d_systems_esp32s3_gen4_r8n16
framework = arduino
lib_deps = 
	adafruit/Adafruit GFX Library@^1.12.5
	adafruit/Adafruit SH110X@^2.1.14
```
