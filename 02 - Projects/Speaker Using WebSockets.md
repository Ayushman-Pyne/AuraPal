---
cssclasses:
  - center-images
---

## Connections
- [[MAX98357A]]
- [[ESP32-S3-N16R8]]

## *HOW TO RUN?*
- Convert the audio `.mp3` to a `.wav` file
- Setup venv and install websockets using `pip install websockets`
- install ffmpeg on windows and run this command `ffmpeg -i song.mp3 -ac 1 -ar 16000 -f wav audio.wav`
- run `server.py`
- upload and run ESP with `platformio.ini` and `main.cpp`

## *Codes*
### ***server.py***
```Python
import asyncio
import websockets
import wave
import time

PORT = 8765
CHUNK = 512

async def stream_audio(websocket):
    print("ESP connected")

    with wave.open("audio.wav", "rb") as wf:
        assert wf.getnchannels() == 1
        assert wf.getsampwidth() == 2
        assert wf.getframerate() == 16000

        start_time = time.time()
        bytes_sent = 0

        while True:
            data = wf.readframes(CHUNK // 2)
            if not data:
                break

            await websocket.send(data)
            bytes_sent += len(data)

            # 🎯 precise timing
            target_time = bytes_sent / 32000.0

            while (time.time() - start_time) < target_time:
                await asyncio.sleep(0.001)

    print("Streaming finished")

async def main():
    async with websockets.serve(
        stream_audio,
        "0.0.0.0",
        PORT,
        ping_interval=None  # 🔥 prevent timeout disconnect
    ):
        print(f"Server running on port {PORT}")
        await asyncio.Future()

asyncio.run(main())
```
### ***platformio.ini***
```ini
[env:esp32-s3-devkitc-1]
platform = espressif32
board = esp32-s3-devkitc-1
framework = arduino

; ===== Serial Monitor =====
monitor_speed = 115200

; ===== Upload =====
upload_speed = 921600

; ===== Libraries =====
lib_deps =
    gilmaimon/ArduinoWebsockets

; ===== Build Flags =====
build_flags =
    -DCORE_DEBUG_LEVEL=3
```

### ***main.cpp***

```C++
#include <Arduino.h>
#include <WiFi.h>
#include <ArduinoWebsockets.h>
#include "driver/i2s.h"

using namespace websockets;

// ===== WiFi =====
const char* ssid = "SystemOverride";
const char* password = "f2cky0ub1tch";

// ===== WebSocket =====
const char* ws_server = "ws://10.77.182.207:8765";
WebsocketsClient client;

// ===== I2S =====
#define I2S_BCLK 38
#define I2S_LRC  39
#define I2S_DOUT 41
#define SAMPLE_RATE 16000

// ===== Ring Buffer =====
#define BUFFER_SIZE 131072
uint8_t buffer[BUFFER_SIZE];

volatile int writeIndex = 0;
volatile int readIndex = 0;

bool started = false;

// ===== I2S Setup =====
void setupI2S() {
    i2s_config_t config = {
        .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_TX),
        .sample_rate = SAMPLE_RATE,
        .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
        .channel_format = I2S_CHANNEL_FMT_RIGHT_LEFT,
        .communication_format = I2S_COMM_FORMAT_STAND_I2S,
        .intr_alloc_flags = 0,
        .dma_buf_count = 8,
        .dma_buf_len = 512,
        .use_apll = false,
        .tx_desc_auto_clear = true
    };

    i2s_pin_config_t pins = {
        .bck_io_num = I2S_BCLK,
        .ws_io_num = I2S_LRC,
        .data_out_num = I2S_DOUT,
        .data_in_num = I2S_PIN_NO_CHANGE
    };

    i2s_driver_install(I2S_NUM_0, &config, 0, NULL);
    i2s_set_pin(I2S_NUM_0, &pins);
}

// ===== Write to Buffer =====
void writeBuffer(const uint8_t* data, int len) {
    for (int i = 0; i < len; i++) {
        buffer[writeIndex] = data[i];
        writeIndex = (writeIndex + 1) % BUFFER_SIZE;

        if (writeIndex == readIndex) {
            readIndex = (readIndex + 1) % BUFFER_SIZE;
        }
    }
}

// ===== WebSocket Handler =====
void onMessage(WebsocketsMessage message) {
    if (message.isBinary()) {
        auto raw = message.rawData(); // std::string
        writeBuffer((uint8_t*)raw.data(), raw.size());
    }
}

// ===== Setup =====
void setup() {
    Serial.begin(115200);

    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(300);
        Serial.print(".");
    }
    Serial.println("\nWiFi Connected");

    setupI2S();

    client.onMessage(onMessage);
    client.connect(ws_server);
}

// ===== Playback Loop =====
void loop() {
    client.poll();

    int available = (writeIndex - readIndex + BUFFER_SIZE) % BUFFER_SIZE;

    // Wait for buffer to fill
    if (!started) {
        if (available > 16000) { // ~0.5 sec buffer
            started = true;
        } else {
            return;
        }
    }

    static int16_t stereo[512 * 2];

    for (int i = 0; i < 512; i++) {
        int16_t sample = 0;

        if (available >= 2) {
            sample = buffer[readIndex] |
                    (buffer[(readIndex + 1) % BUFFER_SIZE] << 8);

            readIndex = (readIndex + 2) % BUFFER_SIZE;
            available -= 2;
        } else {
            sample = 0;
        }

        stereo[2*i]     = sample;
        stereo[2*i + 1] = sample;
    }

    size_t written;
    i2s_write(I2S_NUM_0, stereo, sizeof(stereo), &written, portMAX_DELAY);
}
```


### BONUS (Convert mp3 to raw to a cpp header file to upload the audio directly to the ESP)
- convert to wav `ffmpeg -i song.mp3 -ac 1 -ar 16000 -f wav audio.wav`
- convert to raw `ffmpeg -i audio.wav -f s16le -ac 1 -ar 16000 audio.raw`
- convert to header file using this code: 

```Python
with open("audio.raw", "rb") as f:
    data = f.read()

with open("audio_data.h", "w") as out:
    out.write("const unsigned char audio[] = {\n")

    for i, b in enumerate(data):
        out.write(str(b))

        if i != len(data) - 1:
            out.write(",")

        # new line every 16 values (clean formatting)
        if i % 16 == 15:
            out.write("\n")

    out.write("\n};\n")
    out.write(f"const int audio_len = {len(data)};\n")

print("✅ Written to audio_data.h")
```

