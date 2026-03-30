---
cssclasses:
---

## How to run?

1. Upload the ESP code using platformIO
2. `npm install` in the wsAudioServer folder
3. `npm start` in the wsAudioServer folder
4. go to `http://localhost:8000/audio`


## Codes
### ***platformio.ini***
```ini
[env:esp32-s3-devkitc-1]
platform = espressif32
board = esp32-s3-devkitc-1
framework = arduino
monitor_speed = 115200

  
lib_deps =
    gilmaimon/ArduinoWebsockets@^0.5.3
```

### ***main.cpp***
```C++
#include <Arduino.h>
#include <driver/i2s.h>
#include <WiFi.h>
#include <ArduinoWebsockets.h>
  
#define I2S_WS 15
#define I2S_SD 16
#define I2S_SCK 14
#define I2S_PORT I2S_NUM_0
  
#define bufferCnt 10
#define bufferLen 1024
int16_t sBuffer[bufferLen];
  
const char* ssid = "WIFI_SSID";
const char* password = "WIFI_PASSWORD";
  
const char* websocket_server_host = "IP_ADDRESS"; //ipconfig in cmd
const uint16_t websocket_server_port = 8888;  // <WEBSOCKET_SERVER_PORT>
  
using namespace websockets;
WebsocketsClient client;
bool isWebSocketConnected;
  
// --- Function Prototypes ---
void connectWiFi();
void connectWSServer();
void micTask(void* parameter);
void i2s_install();
void i2s_setpin();
void onEventsCallback(WebsocketsEvent event, String data);
// ---------------------------
  
void onEventsCallback(WebsocketsEvent event, String data) {
  if (event == WebsocketsEvent::ConnectionOpened) {
    Serial.println("Connnection Opened");
    isWebSocketConnected = true;
  } else if (event == WebsocketsEvent::ConnectionClosed) {
    Serial.println("Connnection Closed");
    isWebSocketConnected = false;
  } else if (event == WebsocketsEvent::GotPing) {
    Serial.println("Got a Ping!");
  } else if (event == WebsocketsEvent::GotPong) {
    Serial.println("Got a Pong!");
  }
}
  
void i2s_install() {
  // Set up I2S Processor configuration
  const i2s_config_t i2s_config = {
    .mode = i2s_mode_t(I2S_MODE_MASTER | I2S_MODE_RX),
    .sample_rate = 44100,
    //.sample_rate = 16000,
    .bits_per_sample = i2s_bits_per_sample_t(16),
    .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
    .communication_format = i2s_comm_format_t(I2S_COMM_FORMAT_STAND_I2S),
    .intr_alloc_flags = 0,
    .dma_buf_count = bufferCnt,
    .dma_buf_len = bufferLen,
    .use_apll = false
  };
  
  i2s_driver_install(I2S_PORT, &i2s_config, 0, NULL);
}
  
void i2s_setpin() {
  // Set I2S pin configuration
  const i2s_pin_config_t pin_config = {
    .bck_io_num = I2S_SCK,
    .ws_io_num = I2S_WS,
    .data_out_num = -1,
    .data_in_num = I2S_SD
  };
  i2s_set_pin(I2S_PORT, &pin_config);
}
  
void setup() {
  Serial.begin(115200);
  connectWiFi();
  connectWSServer();
  xTaskCreatePinnedToCore(micTask, "micTask", 10000, NULL, 1, NULL, 1);
}
void loop() {
  // Empty loop
}
  
void connectWiFi() {
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");
}
  
void connectWSServer() {
  client.onEvent(onEventsCallback);
  while (!client.connect(websocket_server_host, websocket_server_port, "/")) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("Websocket Connected!");
}

void micTask(void* parameter) {
  i2s_install();
  i2s_setpin();
  i2s_start(I2S_PORT);
  
  size_t bytesIn = 0;
  while (1) {
    esp_err_t result = i2s_read(I2S_PORT, &sBuffer, bufferLen, &bytesIn, portMAX_DELAY);
    if (result == ESP_OK && isWebSocketConnected) {
      client.sendBinary((const char*)sBuffer, bytesIn);
    }
  }
}
```


### ***server.py*** (instead of node this works)
```Python
import asyncio
import websockets
import json
import os
from flask import Flask, send_from_directory
from vosk import Model, KaldiRecognizer
from threading import Thread
  
# -----------------------------
# CONFIG
# -----------------------------
WS_PORT = 8888
HTTP_PORT = 8000
MODEL_PATH = "model"
  
# -----------------------------
# LOAD VOSK MODEL
# -----------------------------
recognizer = None
  
if os.path.exists(MODEL_PATH):
    print("Loading Vosk model...")
    model = Model(MODEL_PATH)
    recognizer = KaldiRecognizer(model, 44100)
    print("✅ Vosk model loaded")
else:
    print("⚠️ Vosk model not found. Speech recognition disabled.")
  
# -----------------------------
# CLIENT STORAGE
# -----------------------------
connected_clients = set()
  
# -----------------------------
# SAFE SEND (NON-BLOCKING)
# -----------------------------
async def safe_send_all(data):
    dead = set()
  
    for ws in connected_clients:
        try:
            await ws.send(data)
        except:
            dead.add(ws)
  
    connected_clients.difference_update(dead)
  
# -----------------------------
# WEBSOCKET HANDLER
# -----------------------------
async def handler(websocket):
    print("Client connected")
    connected_clients.add(websocket)
  
    try:
        async for data in websocket:
  
            # 🔥 Non-blocking broadcast (fixes stopping issue)
            asyncio.create_task(safe_send_all(data))
  
            # 🔊 Speech recognition
            if recognizer:
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
  
                    if result.get("text"):
                        msg = json.dumps({
                            "type": "transcription",
                            "text": result["text"],
                            "isFinal": True
                        })
                        asyncio.create_task(safe_send_all(msg))
  
                else:
                    partial = json.loads(recognizer.PartialResult())
  
                    if partial.get("partial"):
                        msg = json.dumps({
                            "type": "transcription",
                            "text": partial["partial"],
                            "isFinal": False
                        })
                        asyncio.create_task(safe_send_all(msg))
  
            # 🧠 Prevent event loop blocking
            await asyncio.sleep(0)
  
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")
  
    finally:
        connected_clients.discard(websocket)
  
# -----------------------------
# FLASK SERVER
# -----------------------------
app = Flask(__name__, static_folder="static")
  
@app.route("/audio")
def audio():
    return app.send_static_file("audio_client.html")
  
@app.route("/js/<path:path>")
def js_files(path):
    return send_from_directory("static/js", path)
  
@app.route("/image/<path:path>")
def image_files(path):
    return send_from_directory("static/image", path)
  
# -----------------------------
# START SERVERS
# -----------------------------
async def start_ws():
    async with websockets.serve(handler, "0.0.0.0", WS_PORT):
        print(f"🌐 WebSocket running on ws://localhost:{WS_PORT}")
        await asyncio.Future()  # run forever
  
def start_http():
    print(f"🌐 HTTP server running on http://localhost:{HTTP_PORT}")
    app.run(host="0.0.0.0", port=HTTP_PORT)
  

# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
   Thread(target=start_htp, daemon=True).start()
    asyncio.run(start_ws())
```

