---
cssclasses:
---

## Connections
- [[INMP441]]
- [[ESP32-S3-N16R8]]

## *HOW TO RUN?*
- Setup a venv in Python and install websockets and Flask using 
	- ` python -m venv venv `
	- `.\venv\Scripts\activate`
	- `pip install flask websockets`
- run the server.py using `py server.py`
- upload the `platformio.ini` and `main.cpp`

## *Codes*
### ***server.py***
```Python
import asyncio
import websockets
from flask import Flask, send_from_directory, send_file
import os

# Ports
WS_PORT = 8888
HTTP_PORT = 8000

# Flask app
app = Flask(__name__)

# Store connected clients
connected_clients = set()

# ---------------------------
# WebSocket Server
# ---------------------------
async def handler(websocket):
    print("Connected")
    connected_clients.add(websocket)

    try:
        async for data in websocket:
            # Broadcast to all clients
            dead_clients = set()

            for client in connected_clients:
                try:
                    await client.send(data)
                except:
                    dead_clients.add(client)

            # Remove disconnected clients
            connected_clients.difference_update(dead_clients)

    finally:
        connected_clients.remove(websocket)
        print("Disconnected")


async def start_ws():
    async with websockets.serve(handler, "0.0.0.0", WS_PORT):
        print(f"WS server running at ws://localhost:{WS_PORT}")
        await asyncio.Future()  # run forever


# ---------------------------
# HTTP Server (Flask)
# ---------------------------
@app.route("/image/<path:filename>")
def image(filename):
    return send_from_directory("image", filename)

@app.route("/js/<path:filename>")
def js(filename):
    return send_from_directory("js", filename)

@app.route("/audio")
def audio():
    return send_file(os.path.join(os.getcwd(), "audio_client.html"))


def start_http():
    print(f"HTTP server running at http://localhost:{HTTP_PORT}")
    app.run(host="0.0.0.0", port=HTTP_PORT)


# ---------------------------
# Run both servers together
# ---------------------------
if __name__ == "__main__":
    import threading

    # Start Flask in separate thread
    threading.Thread(target=start_http, daemon=True).start()

    # Run WebSocket server (modern asyncio)
    asyncio.run(start_ws())
```

### ***audio_client.html***
```HTML
<html>
<head>
    <title>PCM Player</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href='http://fonts.googleapis.com/css?family=Roboto' rel='stylesheet' type='text/css'>
    <link rel="icon" href="image/favicon.ico" type="image/x-icon">
    <script src="https://cdn.jsdelivr.net/npm/darkmode-js@1.5.7/lib/darkmode-js.min.js"></script>
    <script src="https://cdn.plot.ly/plotly-latest.min.js" charset="utf-8"></script>
    <script src="https://unpkg.com/pcm-player"></script>
    <script type="js/worker.js"></script>
</head>
<style>
    body {
        font-family: 'Roboto', sans-serif;
    }

    .button {
        border: none;
        padding: 15px 32px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
    }
</style>
<body>
    <h1>ESP32-S3 + I²S Digital Microphone</h1>
    <p>Connect to WebSocket by pressing the [Connect] button first!</p>
    <button id="connectBtn" class="button" onclick="connect()">Connect</button>
    <input type="range" max="1" value="0.5" min="0" id="range" onchange="changeVolume(event)" step="0.1"><br />
    <button id="pauseBtn" class="button" onclick="pause()">Pause Playing</button>
    <button id="continueBtn" class="button" onclick="continuePlay()">Continue Playing</button>
    <div id="graph"></div>
    <script>

    function addDarkmodeWidget() {
        new Darkmode().showWidget();
    }
    window.addEventListener('load', addDarkmodeWidget);

    var connectBtn = document.getElementById("connectBtn");
    var pauseBtn = document.getElementById("pauseBtn");
    var continueBtn = document.getElementById("continueBtn");
    connectBtn.disabled = false;
    pauseBtn.disabled = true;
    continueBtn.disabled = true;

    var worker = new Worker('js/worker.js')
    worker.addEventListener('message', function (e) {
        
        graphDataArray = graphDataArray.concat(e.data)
        graphDataArray.splice(0, 1)

        var data_update = {
            y: [graphDataArray]
        };

        Plotly.update('graph', data_update)
    }, false);

    const arrayLength = 100
    var graphDataArray = []

    for (var i = 0; i < arrayLength; i++) {
        graphDataArray[i] = 0;
    }

    var layout = {
        title: 'Streaming Data',
        paper_bgcolor: "#000",
        plot_bgcolor: "#000",
            xaxis: {
                domain: [0, 1],
                showticklabels: false,
                color: "#FFF",
            },
            yaxis: { domain: [0, 1],
            color: "#FFF",
            rangemode: "auto",
            },
        }

    Plotly.newPlot('graph', [{
        y: graphDataArray,
        mode: 'lines',
        line: { color: '#DF56F1' }
    }], layout);

    let player;
    window.connect = function connect() {

        connectBtn.disabled = !connectBtn.disabled;
        pauseBtn.disabled = !pauseBtn.disabled;

        player = new PCMPlayer({
            inputCodec: 'Int16',
            channels: 1,
            //sampleRate: 16000,
            sampleRate: 44100,
        });
        const WS_URL = 'ws:///10.77.182.207:8888'
        var ws = new WebSocket(WS_URL)
        ws.binaryType = 'arraybuffer'
        ws.addEventListener('message', function (event) {
            if(continueBtn.disabled){
                player.feed(event.data)
                worker.postMessage(event.data) // Remove if it makes the web browser slow.
            }
        });
    }
    window.changeVolume = function changeVolume(e) {
        player.volume(document.querySelector('#range').value)
    }
    window.pause = async function pause() {
        pauseBtn.disabled = true;
        continueBtn.disabled = false;
        await player.pause()
    }
    window.continuePlay = function continuePlay() {
        player.continue()
        pauseBtn.disabled = false;
        continueBtn.disabled = true;
    }
</script>
</body>
</html>
```
### *js/worker.js*
```JavaScript
// worker.js
self.addEventListener('message', function (e) {
   var mean = 0;
   var samples_read = e.data.byteLength / 8;
    if (samples_read > 0) {

        var byteArray = new Int16Array(e.data);

        for (var i = 0; i < samples_read; ++i) {
            mean += (byteArray[i]);
        }

        mean /= samples_read;
        self.postMessage(mean);
    }
}); 
```
### image/favicon.ico
Just the favicon for the website header

### ***platformio.ini***
```ini

[env:esp32-s3-devkitc-1]
platform = espressif32
board = esp32-s3-devkitc-1
framework = arduino
monitor_speed = 115200
lib_deps = 
	gilmaimon/ArduinoWebsockets@^0.5.4
```

### ***main.cpp***
```C++
#include <Arduino.h>
#include <driver/i2s.h>
#include <WiFi.h>
#include <ArduinoWebsockets.h>

// --- Configuration ---
#define I2S_SD 40
#define I2S_WS 39
#define I2S_SCK 38
#define I2S_PORT I2S_NUM_0

#define bufferCnt 10
#define bufferLen 1024
int16_t sBuffer[bufferLen];

const char* ssid = "WIFI_SSID";
const char* password = "WIFI_PASSWORD";
const char* websocket_server_host = "IPADDRESS_FROM_IPCONFIG";
const uint16_t websocket_server_port = 8888;

using namespace websockets;
WebsocketsClient client;
bool isWebSocketConnected = false;

// --- Forward Declarations ---
void onEventsCallback(WebsocketsEvent event, String data);
void i2s_install();
void i2s_setpin();
void connectWiFi();
void connectWSServer();
void micTask(void* parameter);

// --- Functions ---

void onEventsCallback(WebsocketsEvent event, String data) {
  if (event == WebsocketsEvent::ConnectionOpened) {
    Serial.println("Connection Opened");
    isWebSocketConnected = true;
  } else if (event == WebsocketsEvent::ConnectionClosed) {
    Serial.println("Connection Closed");
    isWebSocketConnected = false;
  } else if (event == WebsocketsEvent::GotPing) {
    Serial.println("Got a Ping!");
  } else if (event == WebsocketsEvent::GotPong) {
    Serial.println("Got a Pong!");
  }
}

void i2s_install() {
  const i2s_config_t i2s_config = {
    .mode = i2s_mode_t(I2S_MODE_MASTER | I2S_MODE_RX),
    .sample_rate = 44100,
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
  const i2s_pin_config_t pin_config = {
    .bck_io_num = I2S_SCK,
    .ws_io_num = I2S_WS,
    .data_out_num = -1,
    .data_in_num = I2S_SD
  };

  i2s_set_pin(I2S_PORT, &pin_config);
}

void connectWiFi() {
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected");
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
    esp_err_t result = i2s_read(I2S_PORT, &sBuffer, bufferLen * sizeof(int16_t), &bytesIn, portMAX_DELAY);
    if (result == ESP_OK && isWebSocketConnected) {
      client.sendBinary((const char*)sBuffer, bytesIn);
    }
  }
}

void setup() {
  Serial.begin(115200);
  connectWiFi();
  connectWSServer();
  
  // Create the task on Core 1 (Core 0 usually handles WiFi)
  xTaskCreatePinnedToCore(micTask, "micTask", 10000, NULL, 1, NULL, 1);
}

void loop() {
  // Keep the websocket alive/polling if required by the library
  client.poll();
  delay(10); 
}
```

