import asyncio
import websockets
import json
import os
from flask import Flask, send_from_directory
from vosk import Model, KaldiRecognizer
from threading import Thread

# -----------------------------
# Config
# -----------------------------
WS_PORT = 8888
HTTP_PORT = 8000
MODEL_PATH = "model"

# -----------------------------
# Load Vosk Model
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
# WebSocket Clients
# -----------------------------
connected_clients = set()

# -----------------------------
# Safe broadcast (FIXED)
# -----------------------------
async def safe_send_all(data):
    dead_clients = set()

    for ws in connected_clients:
        try:
            await ws.send(data)
        except:
            dead_clients.add(ws)

    connected_clients.difference_update(dead_clients)

# -----------------------------
# WebSocket Handler
# -----------------------------
async def handler(websocket):
    print("Client connected")
    connected_clients.add(websocket)

    try:
        async for data in websocket:

            # 1. Broadcast raw audio to all clients
            await safe_send_all(data)

            # 2. Speech Recognition
            if recognizer:
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())

                    if result.get("text"):
                        msg = json.dumps({
                            "type": "transcription",
                            "text": result["text"],
                            "isFinal": True
                        })
                        await safe_send_all(msg)

                else:
                    partial = json.loads(recognizer.PartialResult())

                    if partial.get("partial"):
                        msg = json.dumps({
                            "type": "transcription",
                            "text": partial["partial"],
                            "isFinal": False
                        })
                        await safe_send_all(msg)

    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")

    finally:
        connected_clients.discard(websocket)

# -----------------------------
# Flask HTTP Server
# -----------------------------
app = Flask(__name__)

import os

@app.route("/audio")
def audio_client():
    return send_from_directory("static", "audio_client.html")

@app.route("/js/<path:path>")
def send_js(path):
    return send_from_directory("static/js", path)

@app.route("/image/<path:path>")
def send_image(path):
    return send_from_directory("static/image", path)

# -----------------------------
# Run Both Servers
# -----------------------------
async def start_ws():
    async with websockets.serve(handler, "0.0.0.0", WS_PORT):
        print(f"🌐 WebSocket running on ws://localhost:{WS_PORT}")
        await asyncio.Future()  # run forever

def start_http():
    print(f"🌐 HTTP server running on http://localhost:{HTTP_PORT}")
    app.run(host="10.77.182.207", port=HTTP_PORT)

# -----------------------------
# Main
# -----------------------------
if __name__ == "__main__":
    Thread(target=start_http, daemon=True).start()
    asyncio.run(start_ws())